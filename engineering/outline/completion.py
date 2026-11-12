"""Resumable design and city outline completion with bounded process workers.

Only the coordinator writes the execution state. Each city calculation retains
its own geographic inputs, research configuration, price ledger and assumptions.
Compact publications refer to immutable full-run hashes rather than committing
every intermediate engineering object to Git.
"""
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from contextlib import contextmanager
from copy import deepcopy
import fcntl
import gzip
from math import fsum, isfinite
from pathlib import Path
import json
import re
import time
import tomllib
from uuid import uuid4

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.design_search.model_cost import SCOPES
from . import coordinator

PRODUCER = 'engineering/outline/completion.py'
POLICY = 'engineering/outline/completion-policy.toml'
PUBLICATION = 'docs/design-engine/outline-completion'
CASES = ('low', 'base', 'high')
FLAGS = {**coordinator.FLAGS, 'procurement_approved': False,
         'global_optimum_established': False}
_WORKER = None


def seal(value, key='evaluation_id'):
    value[key] = identity(value)
    return value


def policy(root=ROOT):
    value = tomllib.loads((Path(root)/POLICY).read_text())
    if (value.get('schema') != 'osr-outline-completion-policy/1'
            or value.get('physical_reference_changed') is not False
            or value.get('estimates_allowed') is not True):
        raise ValueError('Explicit non-promoting outline completion policy required')
    return value


def _write(path, value):
    path = Path(path)
    _ordinary(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name+'.tmp-'+uuid4().hex)
    temporary.write_bytes(encoded(value))
    temporary.replace(path)


def _ordinary(path):
    path = Path(path)
    if any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Linked completion artifacts are not permitted')
    return path


@contextmanager
def _locked(state):
    state = Path(state)
    _ordinary(state)
    state.mkdir(parents=True, exist_ok=True)
    with _ordinary(state/'coordinator.lock').open('a') as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('Another completion coordinator owns this state') from exc
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _initialize(root, rules, evidence_cache=None):
    global _WORKER
    from . import city_inputs
    root = Path(root)
    _WORKER = dict(root=root, rules=rules, engineering=coordinator.prepare(root),
                   geography=city_inputs.prepare(root))
    if rules.get('civil_water_evidence_comparison',False):
        from . import civil_evidence
        _WORKER['civil_evidence']=civil_evidence.prepare(root,evidence_cache)


def _city(slug):
    from . import city_inputs, city_service, city_project_cost, city_alignment
    context = _WORKER
    root, rules = context['root'], context['rules']
    inputs = city_inputs.load(slug, root=root, context=context['geography'])
    engineering = context['engineering']
    proposals = city_alignment.propose(inputs,root=root,policy=rules)
    experiments = []
    comparison = []
    for variant in proposals['variants']:
        revised = variant['city_input']
        services = city_service.evaluate(revised, rules, engineering['spec']['design'],
                                         engineering['vehicle'], root=root)
        costs = city_project_cost.evaluate_city_cost(
            revised, services['line_services'], engineering, policy=rules, root=root)
        value = _assemble_city(revised, services, costs, engineering, rules)
        eligibility = variant.get('selection_eligibility',{'status':'eligible-outline-hypothesis'})
        comparison.append(dict(kind=variant['kind'],alignment_id=variant['alignment_id'],
            outline_evaluation_id=value['evaluation_id'],selection_eligibility=eligibility,
            route_km=fsum(r['route_m'] for r in revised['lines'])/1000,
            installed_capital_usd=costs['installed_capital_usd'],
            whole_life_npv_usd=costs['whole_life_npv_usd'],
            risk_quantities=variant.get('risk_quantities',{}),
            curvature=[{k:v for k,v in row.items() if k in
                ('line_id','minimum_radius_m','corner_speed_cap_m_s','instant_right_angle_turns','quieter_operation_demonstrated')}
                for row in revised.get('alignment_hypothesis',{}).get('lines',[])
                if 'minimum_radius_m' in row]))
        experiments.append(value)
    eligible = [i for i,row in enumerate(comparison)
                if row['selection_eligibility']['status'] in ('eligible-outline-hypothesis','retained-original')
                and experiments[i]['outline_complete']]
    if not eligible:
        raise ValueError('No coherent outline meets the declared geographic access comparison')
    chosen = min(eligible,key=lambda i:(comparison[i]['whole_life_npv_usd']['base'],comparison[i]['alignment_id']))
    value = deepcopy(experiments[chosen])
    value['source_outline_evaluation_id'] = value.pop('evaluation_id')
    value['alignment_comparison'] = comparison
    value['selected_alignment_id'] = comparison[chosen]['alignment_id']
    value['selected_alignment_kind'] = comparison[chosen]['kind']
    value['alignment_selection_purpose'] = 'Lowest base whole-life calculated cost among access-screened outline hypotheses; not physical adoption'
    value['retained_alignment_experiments'] = [v for i,v in enumerate(experiments) if i!=chosen]
    value['alignment_geometry'] = _alignment_geometry(proposals,experiments)
    value['source_sha256'] = coordinator.merge_sources(value['source_sha256'],proposals['source_sha256'])
    if context.get('civil_evidence'):
        from . import civil_evidence
        chosen_input=value['geometry_and_service']
        report=civil_evidence.evaluate(chosen_input,context['civil_evidence'])
        revised=civil_evidence.revise(chosen_input,report)
        alternate_service=city_service.evaluate(revised,rules,engineering['spec']['design'],engineering['vehicle'],root=root)
        alternate_cost=city_project_cost.evaluate_city_cost(revised,alternate_service['line_services'],engineering,policy=rules,root=root)
        alternate=_assemble_city(revised,alternate_service,alternate_cost,engineering,rules)
        value['civil_comparison']=dict(
            status='comparison-only; not selected for the headline estimate',
            same_route_geometry=True,same_declared_service=True,
            control_city_input_id=chosen_input['input_id'],control_cost_evaluation_id=value['cost']['evaluation_id'],
            alternative_city_input_id=revised['input_id'],alternative_cost_evaluation_id=alternate_cost['evaluation_id'],
            civil_hypothesis_id=revised['civil_hypothesis_id'],
            historical_revision=report['historical_revision'],evidence_report_id=report['evaluation_id'],
            dry_bridge_reclassified_m=report['dry_bridge_reclassified_m'],
            route_m_by_water_status=report['route_m_by_water_status'],
            interface_hold_count=revised['civil_evidence']['interface_hold_count'],
            installed_capital_usd=alternate_cost['installed_capital_usd'],whole_life_npv_usd=alternate_cost['whole_life_npv_usd'],
            price_per_route_km_usd=alternate_cost['price_per_route_km_usd'],
            obstruction_reserve_usd=next(r['costs_usd'] for r in alternate_cost['capital_lines'] if r['key']=='unverified-nonwater-crossing-obstruction-reserve'),
            limitations=report['limitations'],**FLAGS)
        value['civil_evidence_report']=report
        value['retained_civil_experiment']=alternate
        value['source_sha256']=coordinator.merge_sources(value['source_sha256'],alternate['source_sha256'],report['source_sha256'])
    return seal(value)


def _alignment_geometry(proposals,experiments):
    features = []
    for variant,experiment in zip(proposals['variants'],experiments):
        geometry = variant.get('geometry_geojson',{})
        for feature in geometry.get('features',[]):
            feature = deepcopy(feature)
            feature.setdefault('properties',{}).update(variant=variant['kind'],alignment_id=variant['alignment_id'])
            features.append(feature)
        for line in experiment['service_evaluation']['line_services']:
            for stop in line.get('operational_stops',[]):
                features.append(dict(type='Feature',geometry=dict(type='Point',coordinates=[stop['lon'],stop['lat']]),
                    properties=dict(variant=variant['kind'],line_id=line['line_id'],stop_id=stop['id'],
                        role='operational-shared-station-complex',alignment_id=variant['alignment_id'])))
    return dict(type='FeatureCollection',features=features,
        scope='Original and revised outline alignments; no survey, right-of-way, noise or physical acceptance',**FLAGS)


def _assemble_city(inputs, services, costs, context, rules):
    """Add a positive outline result and inspectable delivery handoff."""
    # Source-specific cost validation is performed by the costing adapter. The
    # batch coordinator independently checks coverage and disjoint ledger sums.
    _check_costs(costs)
    if (services['city_input_id']!=inputs['input_id'] or costs['city_input_id']!=inputs['input_id']
            or inputs['reference_candidate_ids']['candidate_id']!=context['vehicle']['candidate_id']):
        raise ValueError('Mixed geographic, service, cost or reference candidate identities')
    sources = coordinator.merge_sources(context['sources'], inputs['source_sha256'],
        services['source_sha256'], costs['source_sha256'])
    lines = services['line_services']
    references = inputs['reference_candidate_ids']
    configuration = dict(reference_candidate_ids=references,
        city_input_id=inputs['input_id'],
        line_research_configurations=[dict(line_id=row['line_id'],
            propulsion_hypothesis=row['propulsion_hypothesis']) for row in lines])
    configuration_id = identity(configuration)
    accepted = bool(lines) and all(row.get('service') and
        row['service']['auxiliary']['energy_balance_screen']=='pass' and
        not row.get('interface_holds') and
        all(leg.get('braking_necessary_distance_fits_leg') is True and
            leg.get('braking_necessary_distance_fits_after_launch') is True for leg in row['legs'])
        for row in lines)
    delivery = dict(schema='osr-city-outline-delivery-draft/1',
        research_configuration_id=configuration_id,
        reference_candidate_ids=references, city_input_id=inputs['input_id'],
        cost_evaluation_id=costs['evaluation_id'],
        quantity_takeoff=costs.get('quantities', costs.get('civil', {})),
        production_and_construction=costs.get('resources', {}),
        phase_order=['survey-and-site-investigation', 'detailed-design-and-independent-review',
                    'factory-setup-and-procurement', 'foundation-and-civil-production',
                    'transport-and-installation', 'power-controls-and-access-installation',
                    'integration-testing-and-release'],
        workforce=dict(production_shifts=2, civil_shifts=2,
            operations_shifts=rules['operations_shifts_per_day'],
            operations_hours_per_day=rules['operating_hours_per_day']),
        procurement_packages=[dict(package_id=identity(dict(configuration_id=configuration_id,line_id=line['line_id'])),
            source_cost_line_id=line['line_id'],name=line['key'],scope=line['scope'],
            estimated_quantities=line['quantity'],budget_usd=line['costs_usd'],
            source_class='calculated-Class-C',supplier_confirmed=False,
            procurement_released=False) for line in costs['capital_lines']],
        manufacturing_routes=[dict(item=row.get('item',row.get('line_key')),
            selected_route=row.get('selected_route'),comparison_id=row.get('comparison',{}).get('evaluation_id'),
            routing_maturity='provisional-calculated',production_released=False)
            for row in costs.get('production_supply',{}).get('decisions',[])],
        ERPNext=dict(disabled=1, submitted=False, external_transactions_performed=False,
            project=dict(name=inputs['city']['name']+' calculated transport outline',status='Draft',
                research_configuration_id=configuration_id),
            draft_BOM_items=[dict(source_cost_line_id=line['line_id'],
                item_name=line['key'],source_quantities=line['quantity'],
                estimated_amount_usd=line['costs_usd']['base'],disabled=1)
                for line in costs['capital_lines']],
            target_site_schema_validation_performed=False),
        Frappe_HR=dict(submitted=False, named_workers_assigned=False,
            production_positions_per_shift=costs.get('resources',{}).get('production_positions_per_shift'),
            workforce_basis='Calculated capacity; employment/shift rosters require site-specific HR validation'),
        controls=dict(movement_authority=False, commissioned=False))
    delivery['draft_id'] = identity(delivery)
    return seal(dict(schema='osr-city-priced-outline/1', city=inputs['city'],
        outline_completion='accepted-calculated-outline' if accepted else 'definition-review-required',
        outline_complete=accepted, research_configuration_id=configuration_id,
        research_configuration=configuration, input_id=inputs['input_id'],
        reference_candidate_ids=references, selection_id=inputs['selection_id'],
        geometry_and_service=inputs, service_evaluation=services, cost=costs,
        delivery_draft=delivery, policy=rules,
        qualification_requirements=['surveyed demand and route/ground conditions',
            'complete installed equipment, structure, fire and accessibility verification',
            'available propulsion force, thermal duty, independent braking and protection',
            'conflict-free service, interfaces, production QA and independent release'],
        source_sha256=sources, **FLAGS))


def _check_costs(value):
    for name in ('installed_capital_usd', 'whole_life_npv_usd'):
        if any(not isfinite(value[name][case]) or value[name][case] <= 0 for case in CASES):
            raise ValueError('Every city needs finite positive complete project prices')
    scope = value['scope_totals_usd']
    if set(scope) != set(SCOPES) or any(scope[s]['base'] < 0 or (scope[s]['base'] == 0 and s != 'renewals') for s in SCOPES):
        raise ValueError('All fourteen city cost scopes must be represented')
    for case in CASES:
        if abs(fsum(scope[s][case] for s in SCOPES)-value['whole_life_npv_usd'][case]) > .1:
            raise ValueError('City whole-life scope sum differs')
        if 'capital_lines' in value:
            cap = fsum(row['costs_usd'][case] for row in value['capital_lines'])
            life = fsum(row['costs_usd'][case] for row in value['lifecycle_lines'])
            if (abs(cap-value['installed_capital_usd'][case])>.1
                    or abs(cap+life-value['whole_life_npv_usd'][case])>.1):
                raise ValueError('City disjoint capital/lifecycle ledger differs')


def _sources(root, geography, engineering, cities=None):
    from . import design_completion
    rows = geography['rows']
    if cities is not None:
        selected = set(cities)
        by_slug = {row['slug']: row for row in rows}
        if not selected or selected - by_slug.keys():
            raise ValueError('Known, nonempty city set required for source binding')
        rows = [by_slug[slug] for slug in sorted(selected)]
    names = (PRODUCER, POLICY, 'engineering/outline/city_inputs.py',
        'engineering/outline/city_service.py', 'engineering/outline/city_civil.py',
        'engineering/outline/city_project_cost.py', 'engineering/outline/design_completion.py',
        'engineering/outline/design_cache.py')
    names += ('engineering/outline/city_alignment.py','engineering/outline/city_cost_inputs.py','engineering/outline/city-cost-inputs.toml','engineering/outline/civil_evidence.py')
    sources = coordinator.merge_sources(geography['source_sha256'], engineering['sources'], design_completion.sources(root),
        {name:digest(Path(root)/name) for name in names})
    # Bind source bytes only for requested cities. The catalogue and its global
    # selection manifests remain in the common map above, while unrelated city
    # payloads need not be read or decompressed for a bounded subset run.
    for row in rows:
        for key in ('geography_path', 'route_geography_path', 'plan_path'):
            name = row.get(key)
            if name:
                sources[name] = digest(Path(root)/name)
        plan = json.loads(gzip.decompress((Path(root)/row['plan_path']).read_bytes()))
        sources = coordinator.merge_sources(sources,plan['source_sha256'])
    return dict(sorted(sources.items()))


def _checked_city(path, request, expected_slug=None):
    value = json.loads(_ordinary(path).read_bytes())
    if (value.get('evaluation_id') != identity({k:v for k,v in value.items() if k!='evaluation_id'})
            or value.get('policy') != request['policy']):
        raise ValueError('Stored city outline identity or policy differs')
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Outline evidence cannot authorize a release')
    if any(request['source_sha256'].get(n)!=sha for n,sha in value['source_sha256'].items()):
        raise ValueError('Stored city outline belongs to a different source epoch')
    slug = value['city']['slug']
    if (expected_slug is not None and slug!=expected_slug
            or value['geometry_and_service']['city']['slug']!=slug
            or value['cost']['city']['slug']!=slug
            or value['input_id']!=value['geometry_and_service']['input_id']
            or value['cost']['city_input_id']!=value['input_id']
            or value['service_evaluation']['city_input_id']!=value['input_id']):
        raise ValueError('City outline geometry, service or requested identity differs')
    _check_costs(value['cost'])
    return value


def _check_sources(root, sources):
    root = Path(root).resolve()
    for name, sha in sources.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Repository-relative source evidence required')
        path = root/relative
        if (any(p.is_symlink() for p in (path,*path.parents) if p!=root)
                or not path.resolve().is_relative_to(root) or digest(path)!=sha):
            raise ValueError('Completion source epoch differs: '+name)


def city_summary(value):
    costs = value['cost']
    inputs = value['geometry_and_service']
    lines = value['service_evaluation']['line_services']
    return dict(city=value['city'], evaluation_id=value['evaluation_id'],
        research_configuration_id=value['research_configuration_id'],
        outline_completion=value['outline_completion'], outline_complete=value['outline_complete'],
        lines=len(lines), route_km=fsum(row['route_m'] for row in inputs['lines'])/1000,
        stations=sum(len(row['stops']) for row in inputs['lines']),
        operational_station_complexes=sum(len(row.get('operational_stops',[])) for row in lines),
        trainsets=sum(row['service']['total_trainsets'] for row in lines),
        installed_capital_usd=costs['installed_capital_usd'],
        whole_life_npv_usd=costs['whole_life_npv_usd'],
        scope_totals_usd=costs['scope_totals_usd'],
        price_per_route_km_usd=costs['price_per_route_km_usd'],
        civil_comparison=value.get('civil_comparison'),
        resources=costs.get('resources', {}),
        selected_alignment_kind=value.get('selected_alignment_kind','original'),
        selected_alignment_id=value.get('selected_alignment_id'),
        alignment_comparison=value.get('alignment_comparison',[]),
        line_outlines=[dict(line_id=row['line_id'],shape=row['shape'],
            headway_s=row['service']['requirements']['headway_s'],
            trainsets=row['service']['total_trainsets'],
            propulsion=row['propulsion_hypothesis']['kind'],
            station_repair=row.get('station_repair',{}),
            known_reference_failures=row.get('known_reference_failures', [])) for row in lines],
        estimate_class='C', **FLAGS)


def run(output, root=ROOT, *, cities=None, workers=2, maximum_cities=None):
    """Resume unchanged sources; keep failures and pending cities explicit."""
    from . import city_inputs, design_completion
    root, output = Path(root).resolve(), Path(output).resolve()
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError('One to four bounded calculation workers required')
    if maximum_cities is not None and (type(maximum_cities) is not int or maximum_cities < 1):
        raise ValueError('Positive invocation city budget required')
    started = time.perf_counter()
    with _locked(output):
        geography = city_inputs.prepare(root)
        available = {row['slug'] for row in geography['rows']}
        slugs = sorted(available if cities is None else set(cities))
        if (not slugs or set(slugs)-available
                or any(not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',s) for s in slugs)):
            raise ValueError('Known, nonempty city set required')
        engineering = coordinator.prepare(root)
        rules = policy(root)
        sources = _sources(root, geography, engineering, slugs)
        request = seal(dict(schema='osr-outline-completion-request/1',cities=slugs,
            policy=rules, source_sha256=sources, **FLAGS),'request_id')
        request_path = output/'request.json'
        if request_path.exists():
            if request_path.read_bytes()!=encoded(request):
                raise ValueError('Source or request changed; use a fresh execution state')
        else:
            _write(request_path, request)
        design_path = output/'designs.json'
        design_cache = dict(cache_hit=False, design_evaluation_performed=False,
            source='existing execution state')
        if not design_path.exists():
            from . import design_cache as design_pricing_cache
            design_value, timing = design_pricing_cache.evaluate_cached(root,
                design_completion_module=design_completion)
            _write(design_path, design_value)
            _write(output/'design-performance.json', timing)
            design_cache = {key:timing[key] for key in (
                'cache_hit','design_evaluation_performed','cache_key','cache_bytes')}
        designs = json.loads(_ordinary(design_path).read_bytes())
        design_completion.validate(designs,root=root)
        if any(sources.get(n)!=sha for n,sha in designs['source_sha256'].items()):
            raise ValueError('Design prices differ from the requested source epoch')
        existing = {}
        for slug in slugs:
            path = output/'cities'/slug/'result.json'
            if path.exists():
                existing[slug] = city_summary(_checked_city(path, request, slug))
        pending = [slug for slug in slugs if slug not in existing]
        chosen = pending if maximum_cities is None else pending[:maximum_cities]
        failures = []
        def record(slug, value=None, error=None):
            if error is not None:
                failure = dict(city=slug, error_type=type(error).__name__, error=str(error),
                    request_id=request['request_id'], retained_for_review=True)
                _write(output/'failures'/(slug+'-'+uuid4().hex+'.json'), failure)
                failures.append(failure)
                return
            _write(output/'cities'/slug/'result.json', value)
            existing[slug] = city_summary(value)
        if workers == 1:
            _initialize(root, rules,output/'civil-evidence-cache')
            for slug in chosen:
                try:
                    record(slug, _city(slug))
                except Exception as exc:
                    record(slug, error=exc)
        elif chosen:
            # At most workers outstanding results; avoid materialising the full
            # network campaign in either worker queues or parent memory.
            with ProcessPoolExecutor(max_workers=workers, initializer=_initialize,
                                     initargs=(str(root),rules,str(output/'civil-evidence-cache'))) as pool:
                iterator = iter(chosen)
                running = {pool.submit(_city,slug):slug for slug in [next(iterator,None) for _ in range(workers)] if slug}
                while running:
                    ready, _ = wait(running, return_when=FIRST_COMPLETED)
                    for future in ready:
                        slug = running.pop(future)
                        try:
                            record(slug, future.result())
                        except Exception as exc:
                            record(slug, error=exc)
                        following = next(iterator, None)
                        if following:
                            running[pool.submit(_city,following)] = following
        _check_sources(root, sources)
        rows = [existing[s] for s in slugs if s in existing]
        summary = seal(dict(schema='osr-outline-completion-summary/1',request_id=request['request_id'],
            policy=rules, cities=rows, requested_cities=len(slugs), completed_cities=len(rows),
            outline_accepted_cities=sum(row['outline_complete'] for row in rows),
            pending_cities=[s for s in slugs if s not in existing],
            designs=designs,
            every_requested_city_priced=len(rows)==len(slugs),
            source_sha256=sources, **FLAGS))
        _write(output/'summary.json', summary)
        files = {'request.json':digest(request_path),'designs.json':digest(design_path),
                 'summary.json':digest(output/'summary.json')}
        files.update({'cities/'+s+'/result.json':digest(output/'cities'/s/'result.json')
                      for s in sorted(existing)})
        manifest = seal(dict(schema='osr-outline-completion-run/1',request_id=request['request_id'],
            evaluation_id=summary['evaluation_id'],files_sha256=files,
            source_sha256=sources, **FLAGS),'manifest_id')
        _write(output/'manifest.json', manifest)
        _write(output/('performance-'+uuid4().hex+'.json'),dict(elapsed_s=time.perf_counter()-started,
            workers=workers,reused_cities=len(rows)-len(chosen)+len(failures),
            attempted_cities=len(chosen),failures=failures,native_solver_calls=0,CAD_jobs=0,
            design_cache=design_cache))
        return manifest


def verify(output, root=ROOT, *, replay=False):
    """Check exact stored artifacts; optionally independently replay every city."""
    output = Path(output)
    manifest = json.loads(_ordinary(output/'manifest.json').read_bytes())
    if (manifest.get('schema')!='osr-outline-completion-run/1'
            or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
            or any(manifest.get(k) is not False for k in FLAGS)):
        raise ValueError('Completion run manifest or disposition differs')
    _check_sources(root,manifest['source_sha256'])
    request = json.loads(_ordinary(output/'request.json').read_bytes())
    expected = {'request.json','designs.json','summary.json'}
    summary = json.loads(_ordinary(output/'summary.json').read_bytes())
    completed = {row['city']['slug'] for row in summary['cities']}
    expected.update('cities/'+s+'/result.json' for s in completed)
    if (set(manifest['files_sha256'])!=expected
            or request.get('request_id')!=manifest['request_id']
            or request['request_id']!=identity({k:v for k,v in request.items() if k!='request_id'})
            or summary['request_id']!=request['request_id']
            or set(request['cities'])!=completed | set(summary['pending_cities'])
            or completed & set(summary['pending_cities'])
            or len(request['cities'])!=summary['requested_cities']
            or request['source_sha256']!=manifest['source_sha256']):
        raise ValueError('Completion artifact set or request differs')
    for name, sha in manifest['files_sha256'].items():
        path = _ordinary(output/name)
        if digest(path)!=sha:
            raise ValueError('Completion artifact differs: '+name)
    _validate_summary(summary)
    from . import design_completion
    designs = json.loads((output/'designs.json').read_bytes())
    design_completion.validate(designs,root=root)
    if encoded(designs)!=encoded(summary['designs']):
        raise ValueError('Stored design prices differ from the summary')
    if summary['evaluation_id']!=manifest['evaluation_id']:
        raise ValueError('Completion summary identity differs')
    if replay:
        _initialize(root,request['policy'],output/'civil-evidence-cache')
        designs,_ = design_completion.evaluate(root=root)
        if encoded(designs)!=(output/'designs.json').read_bytes():
            raise ValueError('Design price completion replay differs')
    for row in summary['cities']:
        slug = row['city']['slug']
        stored = _checked_city(output/'cities'/slug/'result.json',request,slug)
        if encoded(city_summary(stored))!=encoded(row):
            raise ValueError('City summary differs from its complete ledger')
        if replay and encoded(_city(slug))!=encoded(stored):
            raise ValueError('City outline replay differs: '+slug)
    return dict(verified=True,replayed=replay,manifest_id=manifest['manifest_id'],
                completed_cities=len(completed),**FLAGS)


def _validate_summary(summary):
    if (summary.get('schema')!='osr-outline-completion-summary/1'
            or summary.get('evaluation_id')!=identity({k:v for k,v in summary.items() if k!='evaluation_id'})
            or any(summary.get(k) is not False for k in FLAGS)):
        raise ValueError('Completion summary or disposition differs')
    cities = summary['cities']
    slugs = [row['city']['slug'] for row in cities]
    if (len(slugs)!=len(set(slugs)) or len(cities)!=summary['completed_cities']
            or len(summary['pending_cities'])!=len(set(summary['pending_cities']))
            or any(not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',s) for s in slugs+summary['pending_cities'])):
        raise ValueError('Unique city coverage required')
    if (summary['every_requested_city_priced']!=(len(cities)==summary['requested_cities'])
            or len(cities)+len(summary['pending_cities'])!=summary['requested_cities']):
        raise ValueError('Completion coverage differs')
    for row in cities:
        _check_costs(row)
        if any(row.get(k) is not False for k in FLAGS):
            raise ValueError('City outline cannot grant qualification')


def _detail(value, full_sha):
    compact = city_summary(value)
    compact.update(schema='osr-city-outline-summary/1',
        full_result_sha256=full_sha, reference_candidate_ids=value['reference_candidate_ids'],
        input_id=value['input_id'], policy=value['policy'],
        civil_quantities=value['cost'].get('quantities',value['cost'].get('civil',{})),
        assumptions=value['cost'].get('assumptions',{}),
        delivery_draft=value['delivery_draft'],
        qualification_requirements=value['qualification_requirements'],
        source_geography=value['geometry_and_service'].get('source_sha256',{}))
    return compact


def publish(state, output, root=ROOT):
    """Publish compact outputs only after exact full-run verification."""
    state, output = Path(state),Path(output)
    verify(state,root)
    if output.exists():
        raise ValueError('Fresh compact outline completion directory required')
    summary = json.loads((state/'summary.json').read_bytes())
    if (not summary['every_requested_city_priced'] or summary['pending_cities']
            or summary['outline_accepted_cities']!=summary['requested_cities']):
        raise ValueError('Finish every requested city before publishing completion')
    output.mkdir(parents=True)
    _write(output/'summary.json',summary)
    files = {'summary.json':digest(output/'summary.json')}
    full = json.loads((state/'manifest.json').read_bytes())
    for row in summary['cities']:
        slug = row['city']['slug']
        value = json.loads((state/'cities'/slug/'result.json').read_bytes())
        name = 'cities/'+slug+'.json'
        _write(output/name,_detail(value,full['files_sha256']['cities/'+slug+'/result.json']))
        files[name] = digest(output/name)
        map_name = 'maps/'+slug+'.geojson'
        _write(output/map_name,value['alignment_geometry'])
        files[map_name] = digest(output/map_name)
    manifest = seal(dict(schema='osr-outline-completion-publication/1',
        evaluation_id=summary['evaluation_id'],source_sha256=summary['source_sha256'],
        canonical_run_manifest_id=full['manifest_id'],files_sha256=files,
        publication_scope='Calculated city networks and registered component/corridor outlines; not physical acceptance',
        full_run_storage='Private immutable state, reconstruct using engineering.outline complete',
        **FLAGS),'manifest_id')
    _write(output/'manifest.json',manifest)
    return manifest


def verify_publication(output=None, root=ROOT):
    """Bounded read-only verification for the Workbench and reader generator."""
    output = Path(root)/PUBLICATION if output is None else Path(output)
    manifest = json.loads(_ordinary(output/'manifest.json').read_bytes())
    if (manifest.get('schema')!='osr-outline-completion-publication/1'
            or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
            or any(manifest.get(k) is not False for k in FLAGS)):
        raise ValueError('Outline completion publication disposition differs')
    _check_sources(root,manifest['source_sha256'])
    summary = json.loads((output/'summary.json').read_bytes())
    _validate_summary(summary)
    from . import design_completion
    design_completion.validate(summary['designs'],root=root)
    expected = {'summary.json'} | {'cities/'+r['city']['slug']+'.json' for r in summary['cities']}
    expected.update('maps/'+r['city']['slug']+'.geojson' for r in summary['cities'])
    if set(manifest['files_sha256'])!=expected or manifest['evaluation_id']!=summary['evaluation_id']:
        raise ValueError('Outline publication coverage differs')
    for name,sha in manifest['files_sha256'].items():
        if digest(_ordinary(output/name))!=sha:
            raise ValueError('Outline publication payload differs: '+name)
    return manifest,summary
