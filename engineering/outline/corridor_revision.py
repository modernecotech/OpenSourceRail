"""Same-candidate Samawah midpoint comparison over the existing city workflow.

This module constructs an existing typed planning edit and compares authenticated
study records. The caller must obtain records/manifests from CityStudyService's
verified artifact boundary. It performs no solver execution or publication.
"""
from copy import deepcopy
from math import fsum, isfinite
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import city_workflow, planning_adapter, publication_cache
from engineering.design_search.model_cost import SCOPES

PRODUCER = 'engineering/outline/corridor_revision.py'
SCENARIO = 'samawah-line-1-midpoint-consolidation'
RAW_STOP_IDS = ('line-1-0485-0464-s009300', 'line-1-0487-0466-s009380')
NEW_STOP_ID = 'line-1-midpoint-s009339'
_LOADED_SHA = digest(__file__)
FLAGS = {**city_workflow.FLAGS}
CASES = ('low', 'base', 'high')


def _wire_numbers(value):
    """Keep exact requests stable across JSON.stringify's integral numbers.

    Only exactly representable bounded integers change JSON representation;
    fractional geometry coordinates and unknown values are never rounded.
    """
    if isinstance(value, dict):
        return {k: _wire_numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_wire_numbers(v) for v in value]
    if type(value) is float and isfinite(value) and value.is_integer() and abs(value) <= 2**53 - 1:
        return int(value)
    return value


def _seal(value, key):
    value[key] = identity(value)
    return value


def _sealed(value, key, label):
    if not isinstance(value, dict) or value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError('Sealed ' + label + ' required')


def _build_proposal(detail, base, actor, producer_sha):
    seed = detail['planning_seed']
    if base['city'] != 'samawah' or seed['city_slug'] != 'samawah':
        raise ValueError('Published Samawah planning base required')
    template = base['outline_context']['city_input_template']
    line = next(row for row in base['lines'] if row['id'] == 'line-1')
    raw_line = next(row for row in template['lines'] if row['line_id'] == 'line-1')
    raw = {s['id']: s for s in raw_line['stops']}
    pair = [raw[name] for name in RAW_STOP_IDS]
    duty = next(row for row in base['outline_context']['baseline_line_services'] if row['line_id'] == 'line-1')
    complexes = [row for row in duty['station_repair']['complexes']
                 if set(row['original_stop_ids']) == set(RAW_STOP_IDS)]
    if len(complexes) != 1:
        raise ValueError('Exact published two-marker operational complex required')
    complex_id = complexes[0]['operational_stop_id']
    existing = next(s for s in line['stops'] if s['id'] == complex_id)
    if NEW_STOP_ID in {s['id'] for s in line['stops']}:
        raise ValueError('Midpoint proposal stop identity already exists')
    midpoint = fsum(s['chainage_m'] for s in pair) / 2
    separation = abs(pair[1]['chainage_m'] - pair[0]['chainage_m'])
    replacement = [dict(id=s['id'], chainage_m=s['chainage_m'], dwell_s=s['dwell_s'])
                   for s in line['stops']]
    target = next(s for s in replacement if s['id'] == complex_id)
    target.update(id=NEW_STOP_ID, chainage_m=midpoint)
    edit = dict(kind='replace-line-geometry', line='line-1',
                coordinates=deepcopy(line['coordinates']), shape=line['shape'],
                design_speed_cap_m_s=line['design_speed_cap_m_s'], stops=replacement,
                reason='Consolidate the retained close markers at their along-route midpoint')

    def request(edits):
        return city_workflow.normalize(_wire_numbers(dict(city_slug='samawah',
            expected_outline_evaluation_id=detail['evaluation_id'], base_seed_id=seed['seed_id'],
            edit_bundle=dict(schema=planning_adapter.EDIT_SCHEMA, city='samawah',
                base_revision_sha256=base['revision_sha256'], seed_id=seed['seed_id'],
                source_outline_evaluation_id=base['source_outline_evaluation_id'],
                actor=actor, edits=edits))))

    return _seal(dict(schema='osr-corridor-revision-proposal/1', scenario=SCENARIO,
        title='Samawah: retain close markers or consolidate at their midpoint',
        baseline_request=request([]), revised_request=request([edit]),
        reference_candidate_ids=deepcopy(seed['reference_candidate_ids']),
        seed_id=seed['seed_id'], source_outline_evaluation_id=detail['evaluation_id'],
        source_city_input_id=seed['selected_city_input_id'], selection_id=base['selection_id'],
        edit=dict(line_id='line-1', retired_raw_stop_ids=list(RAW_STOP_IDS),
            existing_operational_stop_id=complex_id, proposed_stop_id=NEW_STOP_ID,
            source_chainages_m=[s['chainage_m'] for s in pair],
            separation_m=separation, midpoint_chainage_m=midpoint,
            dwell_s=existing['dwell_s'], route_coordinates_changed=False,
            historical_platform_assumption_m=120,
            platform_assumption_scope='Retained close-station issue; no platform fit or access acceptance is inferred'),
        published_context=dict(raw_marker_count=sum(len(l['stops']) for l in template['lines']),
            operational_stop_count=sum(len(l['operational_stops']) for l in base['outline_context']['baseline_line_services']),
            route_m=fsum(l['route_m'] for l in template['lines']),
            note='The published base already groups the close pair operationally. Raw and operational counts must be reported separately; compact-drive study outcomes are not inherited.'),
        source_sha256={**deepcopy(seed['source_sha256']), PRODUCER: producer_sha}, **FLAGS), 'proposal_id')


def proposal(root=ROOT, actor='v07-samawah-station-merge'):
    """Authenticate the current published seed, then construct the exact edit."""
    root = Path(root)
    if digest(root / PRODUCER) != _LOADED_SHA:
        raise ValueError('Corridor comparison helper changed; restart its caller')
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 200:
        raise ValueError('Bounded named planning actor required')
    detail = publication_cache.json_member('cities/samawah.json.gz', root)
    base = planning_adapter.export_plan(detail['planning_seed'], root=root)
    return _build_proposal(detail, base, actor, _LOADED_SHA)


def _delta(before, after):
    if type(before) in (int, float) and type(after) in (int, float):
        if isfinite(before) and isfinite(after):
            return after - before
        raise ValueError('Finite comparison quantities required')
    if isinstance(before, dict) and isinstance(after, dict):
        return {key: _delta(before.get(key), after.get(key)) for key in sorted(set(before) | set(after))}
    return None


def _case(value, manifest, request, expected):
    _sealed(manifest, 'manifest_id', 'city study manifest')
    _sealed(value, 'evaluation_id', 'city workflow result')
    if (manifest.get('schema') != 'osr-mapped-city-workflow-publication/1'
            or value.get('schema') != 'osr-mapped-city-workflow/1'
            or manifest.get('evaluation_id') != value['evaluation_id']):
        raise ValueError('City study manifest/result identity differs')
    if manifest.get('source_sha256') != value.get('source_sha256'):
        raise ValueError('City study source bindings differ')
    if encoded(value['request']) != encoded(city_workflow.normalize(request)):
        raise ValueError('City study does not match the exact corridor request')
    if (value.get('planning_seed_id') != expected['seed_id']
            or value.get('source_outline_evaluation_id') != expected['source_outline_evaluation_id']):
        raise ValueError('City study belongs to a different planning seed')
    for record, key, name in (
        (value['city_outline'], 'evaluation_id', 'city outline'),
        (value['city_outline']['geometry_and_service'], 'input_id', 'city geometry'),
        (value['city_outline']['service_evaluation'], 'evaluation_id', 'city service'),
        (value['city_outline']['cost'], 'evaluation_id', 'city cost'),
        (value['delivery_plan'], 'plan_id', 'delivery plan'),
        (value['business_drafts'], 'draft_id', 'business drafts'),
    ):
        _sealed(record, key, name)
    city = value['city_outline']; inputs = city['geometry_and_service']
    service = city['service_evaluation']; cost = city['cost']; delivery = value['delivery_plan']
    if (city.get('reference_candidate_ids') != expected['reference_candidate_ids']
            or inputs.get('reference_candidate_ids') != expected['reference_candidate_ids']
            or city.get('selection_id') != expected['selection_id']):
        raise ValueError('Mixed physical candidate or selection in corridor comparison')
    if (city['input_id'] != inputs['input_id'] or service['city_input_id'] != city['input_id']
            or cost['city_input_id'] != city['input_id']
            or delivery['city_input_id'] != city['input_id']
            or delivery['city_record_evaluation_id'] != city['evaluation_id']
            or delivery['cost_evaluation_id'] != cost['evaluation_id']
            or delivery['research_configuration_id'] != city['research_configuration_id']
            or value['business_drafts']['source_plan_id'] != delivery['plan_id']):
        raise ValueError('City study cost/delivery child binding differs')
    if set(cost['scope_totals_usd']) != set(SCOPES):
        raise ValueError('All fourteen cost scopes required')
    city_workflow.completion._check_costs(cost)
    for record in (value, manifest, city):
        if any(record.get(flag) is not False for flag in FLAGS):
            raise ValueError('Corridor comparison cannot grant engineering or operating acceptance')
    return city


def _line_summary(row):
    service = row['service']
    return dict(requirements=deepcopy(row['requirements']), design=deepcopy(row['design']),
        propulsion=deepcopy(row['propulsion_hypothesis']),
        operational_stop_count=len(row['operational_stops']),
        **{k: service.get(k) for k in ('one_way_s', 'round_trip_s', 'active_trainsets',
            'spare_trainsets', 'total_trainsets', 'planning_usable_capacity_pphpd')})


def _numbers(city):
    lines = city['geometry_and_service']['lines']; service = city['service_evaluation']['line_services']
    return dict(raw_marker_count=sum(len(l['stops']) for l in lines),
        operational_stop_count=sum(len(l['operational_stops']) for l in service),
        route_m=fsum(l['route_m'] for l in lines), trainsets=sum(l['service']['total_trainsets'] for l in service),
        installed_capital_usd=city['cost']['installed_capital_usd']['base'],
        whole_life_npv_usd=city['cost']['whole_life_npv_usd']['base'])


def _identities(value, manifest):
    city = value['city_outline']; cost = city['cost']
    return dict(manifest_id=manifest['manifest_id'], workflow_evaluation_id=value['evaluation_id'],
        source_outline_evaluation_id=value['source_outline_evaluation_id'], planning_seed_id=value['planning_seed_id'],
        reference_candidate_ids=deepcopy(city['reference_candidate_ids']), selection_id=city['selection_id'],
        city_input_id=city['input_id'], planning_revision_id=city['planning_revision_id'],
        research_configuration_id=city['research_configuration_id'], city_evaluation_id=city['evaluation_id'],
        service_evaluation_id=city['service_evaluation']['evaluation_id'], cost_evaluation_id=cost['evaluation_id'],
        civil_quantity_id=cost['civil']['quantities']['quantity_id'], delivery_plan_id=value['delivery_plan']['plan_id'],
        business_draft_id=value['business_drafts']['draft_id'])


def compare(proposal, before_value, after_value, before_manifest, after_manifest, *, performance=None):
    """Compare service-verified artifacts; reject mixed requests/candidates.

    File custody is the caller's verified CityStudyService artifact boundary.
    These structural/seal checks do not establish numerical or physical acceptance.
    """
    _sealed(proposal, 'proposal_id', 'corridor proposal')
    if proposal.get('schema') != 'osr-corridor-revision-proposal/1' or proposal.get('scenario') != SCENARIO:
        raise ValueError('Known Samawah midpoint scenario required')
    if proposal.get('source_sha256', {}).get(PRODUCER) != _LOADED_SHA:
        raise ValueError('Corridor proposal belongs to a different helper source')
    if any(proposal.get(flag) is not False for flag in FLAGS):
        raise ValueError('Corridor proposal cannot grant acceptance')
    baseline_request = city_workflow.normalize(proposal['baseline_request'])
    revised_request = city_workflow.normalize(proposal['revised_request'])
    edits = revised_request['edit_bundle']['edits']
    if (baseline_request['edit_bundle']['edits'] != [] or len(edits) != 1
            or edits[0].get('kind') != 'replace-line-geometry'
            or edits[0].get('line') != 'line-1'
            or proposal['edit'].get('retired_raw_stop_ids') != list(RAW_STOP_IDS)
            or proposal['edit'].get('proposed_stop_id') != NEW_STOP_ID):
        raise ValueError('Exact midpoint-only edit proposal required')
    revised_without_edit = deepcopy(revised_request)
    revised_without_edit['edit_bundle']['edits'] = []
    if encoded(revised_without_edit) != encoded(baseline_request):
        raise ValueError('Baseline and revised requests must differ only by the midpoint edit')
    before = _case(before_value, before_manifest, proposal['baseline_request'], proposal)
    after = _case(after_value, after_manifest, proposal['revised_request'], proposal)
    if before_value['source_sha256'] != after_value['source_sha256']:
        raise ValueError('Comparison calculations use different source epochs')
    if encoded(before['policy']) != encoded(after['policy']):
        raise ValueError('Comparison service/pricing policy differs')
    old_lines = {l['line_id']: l for l in before['geometry_and_service']['lines']}
    new_lines = {l['line_id']: l for l in after['geometry_and_service']['lines']}
    if set(old_lines) != set(new_lines):
        raise ValueError('Corridor line identities differ')
    for lid, old in old_lines.items():
        new = new_lines[lid]
        if old['coordinates'] != new['coordinates'] or old['shape'] != new['shape'] or old['route_m'] != new['route_m']:
            raise ValueError('Midpoint consolidation must preserve route geometry')
        old_stops = {s['id']: s for s in old['stops']}; new_stops = {s['id']: s for s in new['stops']}
        removed = set(RAW_STOP_IDS) if lid == 'line-1' else set()
        inserted = {NEW_STOP_ID} if lid == 'line-1' else set()
        if set(old_stops) - removed != set(new_stops) - inserted:
            raise ValueError('Unexpected raw station identity change')
        for sid in set(old_stops) & set(new_stops):
            for field in ('chainage_m', 'lon', 'lat', 'dwell_s'):
                if old_stops[sid].get(field) != new_stops[sid].get(field):
                    raise ValueError('Unexpected unchanged station field revision')
        if lid == 'line-1':
            if not removed <= set(old_stops) or not inserted <= set(new_stops):
                raise ValueError('Required raw station consolidation is missing')
            if abs(new_stops[NEW_STOP_ID]['chainage_m'] - proposal['edit']['midpoint_chainage_m']) > 1e-7:
                raise ValueError('Consolidated station is not at the declared midpoint')
            aliases = new.get('planning_access_aliases', {})
            if any(aliases.get(sid) != NEW_STOP_ID for sid in RAW_STOP_IDS):
                raise ValueError('Retired station access aliases do not bind the midpoint')
    bservice = {l['line_id']: l for l in before['service_evaluation']['line_services']}
    aservice = {l['line_id']: l for l in after['service_evaluation']['line_services']}
    if set(bservice) != set(aservice) or set(bservice) != set(old_lines):
        raise ValueError('Service lines differ from corridor geometry')
    lines = []
    for lid in bservice:
        b, a = _line_summary(bservice[lid]), _line_summary(aservice[lid])
        for field in ('headway_s', 'peak_demand_pphpd', 'operating_hours_per_day',
                      'operating_days_per_year', 'planning_occupancy', 'planning_availability_assumption'):
            if b['requirements'].get(field) != a['requirements'].get(field):
                raise ValueError('Comparison changed fixed service assumption: ' + field)
        if b['design'] != a['design'] or b['propulsion'].get('kind') != a['propulsion'].get('kind'):
            raise ValueError('Comparison changed fixed vehicle/propulsion design')
        lines.append(dict(line_id=lid, before=b, after=a, delta={k: _delta(b[k], a[k])
            for k in ('operational_stop_count', 'one_way_s', 'round_trip_s', 'active_trainsets',
                      'spare_trainsets', 'total_trainsets', 'planning_usable_capacity_pphpd')}))
    bn, an = _numbers(before), _numbers(after)
    labels = dict(raw_marker_count=('Raw station markers', 'count'), operational_stop_count=('Operational station complexes', 'count'),
                  route_m=('Route length', 'm'), trainsets=('Total trainsets', 'count'),
                  installed_capital_usd=('Installed capital, base estimate', 'USD'), whole_life_npv_usd=('Whole-life NPV, base estimate', 'USD'))
    metrics = [dict(key=k, label=labels[k][0], unit=labels[k][1], before=bn[k], after=an[k], delta=_delta(bn[k], an[k])) for k in labels]
    scopes = {k: dict(before=deepcopy(before['cost']['scope_totals_usd'][k]), after=deepcopy(after['cost']['scope_totals_usd'][k]),
                     delta=_delta(before['cost']['scope_totals_usd'][k], after['cost']['scope_totals_usd'][k])) for k in SCOPES}
    quantities = {}
    for group, b, a in (('civil', before['cost']['civil']['quantities'], after['cost']['civil']['quantities']),
                        ('resources', before['cost']['resources'], after['cost']['resources'])):
        for k in sorted(set(b) | set(a)):
            quantities[group + '.' + k] = dict(before=deepcopy(b.get(k)), after=deepcopy(a.get(k)), delta=_delta(b.get(k), a.get(k)), changed=b.get(k) != a.get(k))
    drivers = []
    for group in ('capital_lines', 'lifecycle_lines'):
        b = {l['key']: l for l in before['cost'][group]}; a = {l['key']: l for l in after['cost'][group]}
        for key in sorted(set(b) | set(a)):
            if b.get(key) == a.get(key):
                continue
            drivers.append(dict(group=group, key=key, before=deepcopy(b.get(key)), after=deepcopy(a.get(key)),
                delta_costs_usd=_delta(b.get(key, {}).get('costs_usd'), a.get(key, {}).get('costs_usd'))))
    unresolved = [dict(kind='qualification', before=deepcopy(before.get('qualification_requirements')),
                       after=deepcopy(after.get('qualification_requirements'))),
        dict(kind='pricing', before=deepcopy(before['cost']['assumptions']), after=deepcopy(after['cost']['assumptions'])),
        dict(kind='access', detail='The midpoint changes access hypotheses; actual walking routes, catchments, land and platform interfaces remain unverified.'),
        dict(kind='engineering', detail='This is the published passive-wheel reference, not the retained compact-drive vehicle. Installed vehicle, available-force/braking and manufacturing qualification findings remain open.')]
    for lid in bservice:
        unresolved.append(dict(kind='line-findings', line_id=lid,
            before={k: deepcopy(bservice[lid].get(k)) for k in ('known_reference_failures', 'interface_holds', 'functional_checks')},
            after={k: deepcopy(aservice[lid].get(k)) for k in ('known_reference_failures', 'interface_holds', 'functional_checks')}))
    shared_sources = {n: h for n, h in before_value['source_sha256'].items()
                      if any(t in n for t in ('vehicle', 'development-baseline', 'station_rail'))}
    return _seal(dict(schema='osr-corridor-revision-comparison/1', scenario=SCENARIO,
        proposal_id=proposal['proposal_id'], edit=deepcopy(proposal['edit']), metrics=metrics,
        cost_scopes=scopes, quantities=quantities, cost_drivers=drivers, lines=lines,
        identities=dict(before=_identities(before_value, before_manifest), after=_identities(after_value, after_manifest)),
        reference_candidate_ids=deepcopy(proposal['reference_candidate_ids']), unresolved_inputs=unresolved,
        reuse=dict(vehicle_definition_unchanged=True, manufacturing_reference_inputs_unchanged=True,
            fixed_reference_candidate_ids=deepcopy(proposal['reference_candidate_ids']), shared_vehicle_source_sha256=shared_sources,
            execution_cache_reuse_verified=False,
            scope='Exact same candidate and source inputs; native/cache execution reuse is not inferred from identity equality.'),
        performance=deepcopy(performance),
        explanations=[
            'Both cases use the same published seed and explicit-headway revision evaluator; only the typed midpoint edit differs.',
            'The published city already groups the close raw pair operationally: report raw and operational counts separately, including zero deltas.',
            'Route coordinates and vehicle definition are held fixed; relocation/access allowances and actual derived quantity/cost changes remain explicit.',
            'The retained compact-drive midpoint packet has a different body candidate; none of its fleet or cost outcomes is inherited.'],
        source_sha256={**deepcopy(before_value['source_sha256']), PRODUCER: _LOADED_SHA}, **FLAGS), 'comparison_id')
