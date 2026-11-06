"""Source-bound presentation of calculated city outlines, without physical release.

This is a separate presentation epoch. It replays the existing selected study;
no evaluator, selection rule, input namespace or numerical receipt is changed.
Run ``python -m engineering.outline.city_atlas compile OUTPUT`` and ``verify``.
"""
from copy import deepcopy
from math import fsum
from pathlib import Path
import argparse
import json
import re

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.development_baseline import planning
from engineering.development_baseline.planning import _gzip_member
from . import completion, completion_publication, planning_adapter, planning_geometry

PRODUCER = 'engineering/outline/city_atlas.py'
SCHEMA = 'osr-city-atlas/1'
PUBLICATION = 'docs/design-engine/city-atlas'
FLAGS = {**completion.FLAGS, 'physical_reference_changed': False,
         'timetable_qualified': False, 'independent_braking_qualified': False}


def _presentation_sources():
    return {PRODUCER:digest(__file__), **{module.PRODUCER:digest(module.__file__)
        for module in (planning_adapter, planning_geometry, completion, completion_publication)},
        'engineering/development_baseline/planning.py':digest(planning.__file__)}


def _sealed(value, key):
    if value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError('City atlas source identity differs: '+key)


def _no_release(value):
    if any(value.get(k) not in (None, False) for k in FLAGS):
        raise ValueError('City atlas cannot grant physical or operating release')


def _point(stop):
    return [stop['lon'], stop['lat']]


def _complexes(line, duty):
    raw = {s['id']: s for s in line['stops']}
    operational = {s['id']: s for s in duty['operational_stops']}
    chain = line.get('coordinate_chainages_m') or planning_geometry.route(line['coordinates'], line['shape'])
    output = []
    for source in duty['station_repair']['complexes']:
        row = deepcopy(source)
        stop = operational[row['operational_stop_id']]
        row['coordinates'] = _point(stop)
        row['original_markers'] = [deepcopy(raw[s]) for s in row['original_stop_ids']]
        row['access_connectors'] = [dict(original_stop_id=walk['original_stop_id'],
            from_coordinates=_point(raw[walk['original_stop_id']]), to_coordinates=_point(stop),
            along_route_connector_m=walk['along_route_connector_m'],
            geometry_basis='Schematic endpoint connector; actual accessible path is not surveyed')
            for walk in row['original_marker_walks']]
        platforms = []
        for low, high in row['boarding_platform_intervals_m']:
            # Radial terminal platform intervals may extend beyond the route.
            # Clip only the drawable part; preserve the full declared intervals.
            a, b = max(0., low), min(chain[-1], high)
            if a <= b:
                inside = [list(p) for at, p in zip(chain, line['coordinates']) if a < at < b]
                platforms.append([planning_geometry.point(line['coordinates'], chain, a), *inside,
                                  planning_geometry.point(line['coordinates'], chain, b)])
        row['platform_coordinates'] = platforms
        row['platform_geometry_basis'] = 'Declared chainage envelope on route centreline; track/platform engineering unverified'
        output.append(row)
    return output


def build_record(detail, geometry=None, city=None, service=None, cost=None):
    """Build from a published detail plus replay, or an exact workflow record.

    Caller authenticates the publication/run manifest before calling. A completed
    workflow record may be passed as ``detail`` with the other values omitted.
    All numeric and geometry inputs are preserved under their original IDs.
    """
    if city is None:
        city, service, cost = (detail['geometry_and_service'], detail['service_evaluation'], detail['cost'])
    if geometry is None:
        geometry = detail.get('alignment_geometry', dict(type='FeatureCollection', features=[]))
    for record, key in ((city, 'input_id'), (service, 'evaluation_id'), (cost, 'evaluation_id')):
        _sealed(record, key)
        _no_release(record)
    _no_release(detail)
    if (city['city'] != detail['city'] or service['city_input_id'] != city['input_id']
            or cost['city_input_id'] != city['input_id']
            or cost.get('input_line_services_id') != identity(service['line_services'])
            or detail['reference_candidate_ids'] != city['reference_candidate_ids']):
        raise ValueError('Mixed city atlas city, service, cost or physical candidate')
    seed = detail.get('planning_seed', {})
    if seed:
        _sealed(seed, 'seed_id')
        expected = dict(selected_city_input_id=city['input_id'], selected_service_evaluation_id=service['evaluation_id'],
            source_cost_evaluation_id=cost['evaluation_id'], source_outline_evaluation_id=detail['evaluation_id'],
            selected_alignment_id=detail.get('selected_alignment_id'),
            research_configuration_id=detail['research_configuration_id'], reference_candidate_ids=city['reference_candidate_ids'])
        if any(seed.get(k) != v for k, v in expected.items()):
            raise ValueError('City atlas replay differs from published seed')
    completion._check_costs(cost)
    duties = {r['line_id']: r for r in service['line_services']}
    if len(duties) != len(service['line_services']) or set(duties) != {r['line_id'] for r in city['lines']}:
        raise ValueError('Exactly one atlas service per line required')
    lines = []
    for line in city['lines']:
        duty = duties[line['line_id']]
        s, req, design = duty['service'], duty['requirements'], duty['design']
        days, hours, headway = req['operating_days_per_year'], req['operating_hours_per_day'], req['headway_s']
        metrics = {k: deepcopy(s[k]) for k in ('capacity_pphpd', 'planning_usable_capacity_pphpd',
            'normal_places_per_train', 'one_way_s', 'round_trip_s', 'cycle_per_direction_s',
            'active_trainsets', 'spare_trainsets', 'total_trainsets', 'totalcars', 'train_km_per_day',
            'mechanical_work_kwh_per_departure', 'mechanical_work_kwh_per_direction_trip',
            'peak_train_force_N', 'peak_train_mechanical_power_W') if k in s}
        metrics.update(headway_s=headway, peak_demand_pphpd=req['peak_demand_pphpd'],
            demand_source=req.get('demand_source', service.get('assumptions', {}).get('demand_source')),
            annual_train_km=s['train_km_per_day']*days,
            mechanical_traction_kwh_per_day=s['mechanical_work_kwh_per_direction_trip']*2*3600/headway*hours,
            auxiliary_load_kwh_per_day=s['active_trainsets']*6*design['aux_kw_per_car']*hours,
            auxiliary_grid_kwh_per_day=s['active_trainsets']*6*design['aux_kw_per_car']*hours/design['charge_efficiency'],
            electrical_traction_kwh_per_day=None,
            total_electrical_energy_kwh_per_day=None,
            energy_basis='Mechanical traction and nominal active-fleet hotel energy; electrical traction, station and depot energy require their scenario-specific efficiencies/loads. Cost ledger retains priced scenarios.')
        row = deepcopy(line)
        row.update(original_stops=deepcopy(line['stops']), operational_stops=deepcopy(duty['operational_stops']),
            station_complexes=_complexes(line, duty), legs=deepcopy(duty['legs']),
            requirements=deepcopy(req), design=deepcopy(design), service=deepcopy(s),
            propulsion_hypothesis=deepcopy(duty['propulsion_hypothesis']), metrics=metrics,
            station_repair=deepcopy(duty['station_repair']),
            known_reference_failures=deepcopy(duty.get('known_reference_failures', [])),
            interface_holds=deepcopy(duty.get('interface_holds', [])),
            service_evaluation_id=duty['evaluation_id'])
        lines.append(row)
    calculation = planning_adapter.merge_sources(detail.get('source_sha256', seed.get('source_sha256', {})),
        city.get('source_sha256', {}), service.get('source_sha256', {}), cost.get('source_sha256', {}))
    identities = dict(outline_evaluation_id=detail['evaluation_id'], city_input_id=city['input_id'],
        service_evaluation_id=service['evaluation_id'], cost_evaluation_id=cost['evaluation_id'],
        selected_alignment_id=detail.get('selected_alignment_id'), selected_alignment_kind=detail.get('selected_alignment_kind'),
        research_configuration_id=detail['research_configuration_id'], selection_id=city['selection_id'],
        reference_candidate_ids=deepcopy(city['reference_candidate_ids']),
        source_result_sha256=detail.get('full_result_sha256', seed.get('source_result_sha256')),
        seed_id=seed.get('seed_id'))
    costs = {k: deepcopy(cost[k]) for k in ('installed_capital_usd', 'whole_life_npv_usd', 'scope_totals_usd',
        'price_per_route_km_usd', 'capital_lines', 'lifecycle_lines', 'pricing_basis', 'energy_ledger', 'local_cost_inputs') if k in cost}
    packet = dict(schema=SCHEMA, city=deepcopy(city['city']), identity=identities,
        sources=dict(calculation_sha256=calculation, presentation_sha256=_presentation_sources()),
        geometry=deepcopy(geometry), lines=lines, interchanges=deepcopy(city.get('interchanges', [])),
        summary=dict(lines=len(lines), route_km=fsum(l['route_m'] for l in lines)/1000,
            original_stop_records=sum(len(l['original_stops']) for l in lines),
            operational_station_complexes=sum(len(l['operational_stops']) for l in lines),
            total_trainsets=sum(l['service']['total_trainsets'] for l in lines),
            train_km_per_day=fsum(l['metrics']['train_km_per_day'] for l in lines),
            annual_train_km=fsum(l['metrics']['annual_train_km'] for l in lines)),
        costs=costs, civil={k: deepcopy(v) for k,v in cost.get('civil', {}).items()
            if k not in ('source_sha256', 'sources', 'unit_rates')},
        resources=deepcopy(cost.get('resources', {})),
        assumptions=dict(service=deepcopy(service.get('assumptions', {})), cost=deepcopy(cost.get('assumptions', {})),
            policy=deepcopy(detail.get('policy', seed.get('rules', {})))),
        missing_evidence=deepcopy(detail.get('qualification_requirements', [])),
        evidence=dict(execution='replayed-calculated-outline', numerical_validity='existing-evaluator-contract',
            engineering_screen=detail.get('outline_completion'), evidence_maturity='calculated-Class-C',
            selection_purpose=detail.get('alignment_selection_purpose', 'Existing published outline selection; no new selection'),
            physical_acceptance='open', surveyed_demand_available=False, physical_measurements_added=False), **FLAGS)
    packet['missing_evidence'] += ['Authenticated available-force, brake, charge and thermal maps',
        'Surveyed accessible station paths, platforms and route/ground/clearance data',
        'Complete installed mass and equipment interfaces; independently reviewed physical qualification',
        'Local supplier quotes, workforce/land/utilities validation and conflict-free timetable']
    contexts = [(name, sha) for name, sha in city.get('source_sha256', {}).items()
                if name.endswith('/map-context.json.gz')]
    if len(contexts) == 1:
        packet['map_context'] = dict(path=contexts[0][0], sha256=contexts[0][1],
            role='Geographic context only; no survey, demand, route clearance or physical qualification')
    packet['packet_id'] = identity(packet)
    return packet


def from_study(value, geometry=None):
    """Adapt an already verified city_workflow result without any recalculation.

    The caller must first authenticate the immutable job with city_workflow.verify.
    Hash checks here establish internal consistency, not caller authentication.
    """
    _sealed(value, 'evaluation_id'); _no_release(value)
    if value.get('schema') != 'osr-mapped-city-workflow/1' or value.get('calculation_complete') is not True:
        raise ValueError('Completed verified mapped-city workflow required')
    selected = value['city_outline']
    _sealed(selected, 'evaluation_id')
    if value['city'] != selected['city']:
        raise ValueError('Mixed workflow and selected city')
    if geometry is None:
        variants = dict(variants=[dict(kind=c['kind'], alignment_id=c['alignment_id'],
            geometry_geojson=dict(type='FeatureCollection', features=[dict(type='Feature',
                properties=dict(line_id=line['line_id']), geometry=dict(type='LineString', coordinates=line['coordinates']))
                for line in c['record']['geometry_and_service']['lines']])) for c in value['cases']])
        geometry = completion._alignment_geometry(variants, [c['record'] for c in value['cases']])
    packet = build_record(selected, geometry)
    packet['identity'].update(workflow_evaluation_id=value['evaluation_id'],
        source_result_sha256=identity(value), planning_revision_id=selected.get('planning_revision_id'))
    packet['sources']['calculation_sha256'] = planning_adapter.merge_sources(
        packet['sources']['calculation_sha256'], value.get('source_sha256', {}))
    packet['evidence']['execution'] = 'existing-completed-city-workflow'
    packet.pop('packet_id'); packet['packet_id'] = identity(packet)
    return packet


def _write_gzip(path, value):
    path = completion._ordinary(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name+'.tmp')
    temporary.write_bytes(_gzip_member(encoded(value)))
    temporary.replace(path)


def _read(path):
    return completion_publication.read_json(path)


def _row(packet):
    return dict(city=packet['city'], packet_id=packet['packet_id'], identity=packet['identity'],
        **packet['summary'], installed_capital_usd=packet['costs']['installed_capital_usd'],
        whole_life_npv_usd=packet['costs']['whole_life_npv_usd'], **FLAGS)


def compile(output, root=ROOT, *, cities=None, maximum_cities=None, state=None):
    """Resume per-city atomic packets, authenticating the complete catalogue first."""
    from . import city_inputs, coordinator, city_project_cost
    root, output = Path(root).resolve(), Path(output).resolve()
    published, catalogue = completion_publication.verify(root=root)
    execution=None
    if state is not None:
        state=Path(state).resolve()
        verification=completion.verify(state,root=root)
        execution=json.loads(completion._ordinary(state/'manifest.json').read_bytes())
        _sealed(execution,'manifest_id')
        if execution['manifest_id']!=verification['manifest_id'] or execution['manifest_id']!=published.get('canonical_run_manifest_id'):
            raise ValueError('Atlas execution differs from the published canonical run')
    available = {r['city']['slug'] for r in catalogue['cities']}
    slugs = sorted(available if cities is None else set(cities))
    if not slugs or set(slugs)-available:
        raise ValueError('Known nonempty atlas cities required')
    if maximum_cities is not None and (type(maximum_cities) is not int or maximum_cities < 1):
        raise ValueError('Positive invocation city budget required')
    request = dict(schema=SCHEMA+'/request', cities=slugs, publication_manifest_id=published['manifest_id'],
        catalogue_id=catalogue['catalogue_id'], presentation_sha256=_presentation_sources(), **FLAGS)
    if execution is not None:request['execution_manifest_id']=execution['manifest_id']
    request['request_id'] = identity(request)
    with completion._locked(output):
        if (output/'request.json').exists():
            if json.loads((output/'request.json').read_bytes()) != request:
                raise ValueError('Atlas request/source epoch changed; use a fresh output directory')
        else:
            completion._write(output/'request.json', request)
        context = None
        rows, files, pending = [], {'request.json':digest(output/'request.json')}, []
        made = 0
        for slug in slugs:
            name = 'cities/'+slug+'.json.gz'
            path = output/name
            if path.exists():
                packet = _read(path)
                _sealed(packet, 'packet_id'); _no_release(packet)
                if (packet['city']['slug'] != slug or packet['sources']['publication_manifest_id'] != published['manifest_id']
                        or packet['sources']['presentation_sha256'] != request['presentation_sha256']):
                    raise ValueError('Stale resumed atlas packet: '+slug)
            elif maximum_cities is not None and made >= maximum_cities:
                pending.append(slug); continue
            else:
                if context is None and execution is None:
                    context = dict(engineering=coordinator.prepare(root), geography=city_inputs.prepare(root))
                try:
                    detail = _read(root/completion_publication.PUBLICATION/'cities'/ (slug+'.json.gz'))
                    geometry = _read(root/completion_publication.PUBLICATION/'maps'/ (slug+'.geojson.gz'))
                    seed = detail['planning_seed']
                    if execution is None:
                        city, service = planning_adapter._reconstruct(seed, root, context, verify_cost=True)
                        cost = city_project_cost.evaluate_city_cost(city, service['line_services'], context['engineering'], policy=seed['rules'], root=root)
                    else:
                        full_name='cities/'+slug+'/result.json';full_path=completion._ordinary(state/full_name)
                        if digest(full_path)!=execution['files_sha256'].get(full_name) or digest(full_path)!=detail['full_result_sha256']:
                            raise ValueError('Atlas city execution differs from published full result')
                        full=json.loads(full_path.read_bytes())
                        if full['evaluation_id']!=detail['evaluation_id'] or full['alignment_geometry']!=geometry:
                            raise ValueError('Atlas execution outline or geometry differs')
                        city,service,cost=full['geometry_and_service'],full['service_evaluation'],full['cost']
                    packet = build_record(detail, geometry, city, service, cost)
                    if execution is not None:
                        packet['sources']['execution_manifest_id']=execution['manifest_id']
                        packet['evidence']['execution']='verified-completed-outline; no fresh numerical replay'
                    packet['sources'].update(publication_manifest_id=published['manifest_id'], catalogue_id=catalogue['catalogue_id'])
                    packet.pop('packet_id'); packet['packet_id'] = identity(packet)
                    _write_gzip(path, packet)
                    made += 1
                except Exception as exc:
                    completion._write(output/'failures'/(slug+'.json'), dict(city_slug=slug,
                        request_id=request['request_id'], error_type=type(exc).__name__, error=str(exc), **FLAGS))
                    raise
            rows.append(_row(packet)); files[name] = digest(path)
        summary = dict(schema=SCHEMA+'/catalogue', request_id=request['request_id'],
            requested_cities=len(slugs), completed_cities=len(rows), pending_cities=pending,
            every_requested_city_compiled=not pending, cities=rows, **FLAGS)
        summary['catalogue_id'] = identity(summary)
        completion._write(output/'summary.json', summary); files['summary.json'] = digest(output/'summary.json')
        manifest = dict(schema=SCHEMA+'/manifest', request_id=request['request_id'],
            publication_manifest_id=published['manifest_id'], source_catalogue_id=catalogue['catalogue_id'],
            catalogue_id=summary['catalogue_id'], files_sha256=files,
            calculation_sha256=published['source_sha256'], presentation_sha256=request['presentation_sha256'],
            publication_scope='Source-bound presentation only; existing calculated outlines; no new selection or qualification', **FLAGS)
        manifest['manifest_id'] = identity(manifest)
        completion._write(output/'manifest.json', manifest)
    return manifest, summary


def verify(output=None, root=ROOT):
    output = Path(root)/PUBLICATION if output is None else Path(output)
    published, catalogue = completion_publication.verify(root=root)
    manifest = json.loads(completion._ordinary(output/'manifest.json').read_bytes())
    _sealed(manifest, 'manifest_id'); _no_release(manifest)
    if (manifest.get('schema') != SCHEMA+'/manifest' or manifest['publication_manifest_id'] != published['manifest_id']
            or manifest['source_catalogue_id'] != catalogue['catalogue_id']):
        raise ValueError('Atlas source publication differs')
    completion._check_sources(root, manifest['calculation_sha256'])
    if manifest['presentation_sha256'] != _presentation_sources():
        raise ValueError('Atlas presentation source changed')
    for name, sha in manifest['files_sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or digest(completion._ordinary(output/name)) != sha:
            raise ValueError('Atlas artifact differs: '+name)
    request = json.loads((output/'request.json').read_bytes())
    summary = json.loads((output/'summary.json').read_bytes())
    _sealed(request, 'request_id'); _sealed(summary, 'catalogue_id')
    _no_release(request); _no_release(summary)
    if (summary['catalogue_id'] != manifest['catalogue_id'] or request['request_id'] != manifest['request_id']
            or summary['request_id'] != request['request_id']):
        raise ValueError('Atlas request/catalogue identity differs')
    expected = {'request.json', 'summary.json'}
    completed = []
    for row in summary['cities']:
        slug = row['city']['slug']
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError('Invalid atlas slug')
        name = 'cities/'+slug+'.json.gz'; expected.add(name)
        packet = _read(output/name); _sealed(packet, 'packet_id'); _no_release(packet)
        if (packet.get('schema') != SCHEMA or _row(packet) != row
                or packet['sources']['publication_manifest_id'] != published['manifest_id']
                or packet['sources']['presentation_sha256'] != manifest['presentation_sha256']):
            raise ValueError('Atlas city binding differs: '+slug)
        completion._check_costs(packet['costs']); completed.append(slug)
    if (set(manifest['files_sha256']) != expected or len(completed) != len(set(completed))
            or summary['completed_cities'] != len(completed)
            or summary['requested_cities'] != len(request['cities'])
            or set(completed) & set(summary['pending_cities'])
            or sorted(completed+summary['pending_cities']) != request['cities']
            or summary['every_requested_city_compiled'] != (not summary['pending_cities'])):
        raise ValueError('Atlas city coverage differs')
    return manifest, summary


publish = compile


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('compile', 'publish', 'verify'))
    parser.add_argument('output', type=Path)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--city', action='append', dest='cities')
    parser.add_argument('--maximum-cities', type=int)
    parser.add_argument('--state', type=Path, help='Exact verified canonical execution; reuse completed calculations')
    args = parser.parse_args(argv)
    result = (verify(args.output, args.root) if args.action == 'verify' else
              compile(args.output, args.root, cities=args.cities, maximum_cities=args.maximum_cities,state=args.state))
    print(json.dumps(dict(manifest_id=result[0]['manifest_id'], completed_cities=result[1]['completed_cities'],
        pending_cities=result[1]['pending_cities']), sort_keys=True))


if __name__ == '__main__':
    main()
