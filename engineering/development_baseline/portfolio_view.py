"""Read-only projections of current, separately scoped research portfolios.

This reader executes no engineering model and performs no new ranking. It joins
existing mechanics through the exact parent portfolio and quantity evaluation,
keeping the quantity and mechanics archives distinct.
"""
from copy import deepcopy
from collections import Counter
import gzip
from hashlib import sha256
import json
from math import isfinite
import re

from engineering.station_rail.common import identity
from .entrypoint import CurrentUnavailable, checked_path

FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    configuration_adopted=False, selected_reference_changed=False,
    manufacturing_release=False, operating_release=False)


def _research(record):
    if (any(record.get(key) is not False for key in FLAGS if key != 'selected_reference_changed')
            or record.get('selected_reference_changed', False) is not False
            or record.get('integrated_selection') is not None):
        raise CurrentUnavailable('Portfolio research cannot confer acceptance or selection')


def _sealed(record, key):
    if record.get(key) != identity({k: v for k, v in record.items() if k != key}):
        raise CurrentUnavailable('Portfolio record identity differs: ' + key)


def _read(root, publication, folder, filename, schema, key):
    relative = 'docs/design-engine/' + folder + '/' + filename
    raw = checked_path(root, relative).read_bytes()
    if publication.get('source_sha256', {}).get(relative) != sha256(raw).hexdigest():
        raise CurrentUnavailable('Portfolio payload lacks a current source binding: ' + relative)
    value = json.loads(gzip.decompress(raw) if filename.endswith('.gz') else raw)
    if value.get('schema') != schema:
        raise CurrentUnavailable('Portfolio schema differs: ' + relative)
    _sealed(value, key)
    _research(value)
    return value


def _rows(record, sealed=False):
    rows = record['evaluations']
    by_id = {row['candidate_id']: row for row in rows}
    if (len(by_id) != len(rows) or len(rows) != record['candidate_count']
            or not rows or any(re.fullmatch('[a-f0-9]{64}', key) is None for key in by_id)):
        raise CurrentUnavailable('Unique portfolio candidate coverage required')
    for row in rows:
        _research(row)
        if sealed:
            _sealed(row, 'evaluation_id')
    return by_id


def _archive(record, by_id):
    archive = record['archive']
    _sealed(archive, 'archive_id')
    if archive.get('integrated_selection') is not None or archive.get('global_optimum_proven') is not False:
        raise CurrentUnavailable('Portfolio archive cannot select a railway')
    members, retained, excluded = [], [], {}
    for cell in archive['cells']:
        members.extend(cell['candidate_ids'])
        retained.extend(cell['retained_pareto_candidate_ids'])
        for row in cell['excluded']:
            excluded[row['candidate_id']] = row['dominated_by']
    if (len(members) != len(set(members)) or set(members) != set(by_id)
            or len(retained) != len(set(retained)) or not set(retained) <= set(by_id)
            or sorted(retained) != archive['retained_candidate_ids']
            or set(excluded) != set(by_id) - set(retained)
            or any(not values or not set(values) <= set(by_id) for values in excluded.values())):
        raise CurrentUnavailable('Portfolio archive candidate coverage differs')
    return set(retained), excluded


def project(body, civil, mechanics, baseline, topology=None, topology_revisions=None, topology_parent_binding=None):
    """Join authenticated input records; never compare costs across their scopes."""
    bodies = _rows(body)
    civils = _rows(civil, sealed=True)
    mechanical = _rows(mechanics, sealed=True)
    for record, key in ((body, 'portfolio_id'), (civil, 'portfolio_id'), (mechanics, 'study_id')):
        _sealed(record, key)
        _research(record)
    quantity_body, excluded_body = _archive(body, bodies)
    quantity_civil, excluded_civil = _archive(civil, civils)
    mechanical_retained, _ = _archive(mechanics, mechanical)
    context = mechanics['load_context']
    vehicle = baseline['vehicle']
    if (mechanics['parent_portfolio_id'] != civil['portfolio_id']
            or set(mechanical) != set(civils)
            or context['selection_id'] != baseline['selection_id']
            or context['vehicle_candidate_id'] != vehicle['candidate_id']
            or context['vehicle_evaluation_id'] != vehicle['evaluation_id']
            or mechanics['stage_1_complete'] is not False):
        raise CurrentUnavailable('Civil mechanics parent portfolio or selected load identity differs')
    _sealed(context, 'context_id')
    cases = {}
    for case in mechanics['cases']:
        _sealed(case, 'evaluation_id')
        _research(case)
        cid = case['candidate_id']
        if (cid not in civils or case['quantity_evaluation_id'] != civils[cid]['evaluation_id']
                or case['load_context_id'] != context['context_id'] or case['evaluation_id'] in cases):
            raise CurrentUnavailable('Civil mechanics quantity evaluation or load identity differs')
        cases[case['evaluation_id']] = case
    if len(cases) != mechanics['calculated_case_count']:
        raise CurrentUnavailable('Civil mechanics case count differs')
    indexed_cases = []
    for cid, row in mechanical.items():
        ids = row['case_evaluation_ids']
        if (not ids or len(ids) != len(set(ids))
                or any(key not in cases or cases[key]['candidate_id'] != cid for key in ids)
                or row['load_context_id'] != context['context_id']
                or row['stage_1_complete'] is not False or row['stage_2_admission'] is not False):
            raise CurrentUnavailable('Civil mechanics candidate cases or admission differs')
        indexed_cases.extend(ids)
    if len(indexed_cases) != len(cases) or set(indexed_cases) != set(cases):
        raise CurrentUnavailable('Civil mechanics candidate case coverage differs')

    body_rows = []
    for cid, row in bodies.items():
        cost = row['cost_estimate']
        if cost['candidate_id'] != cid or row['mass_properties']['candidate_id'] != cid:
            raise CurrentUnavailable('Body cost or mass candidate identity differs')
        screen = row['interface_screen']
        issues = Counter((issue['code'], issue['status']) for issue in screen['issues'])
        body_rows.append(dict(candidate_id=cid, definition_id=row['definition_id'],
            quantity_record_sha256=identity(row), quantity_evaluation_id=None,
            descriptor=deepcopy(row['descriptor']), profile=row['profile_id'],
            stock_mass_kg=row['metrics']['known_gross_structure_stock_kg'],
            cost_iqd=deepcopy(cost['scenarios_iqd']), process_hours=deepcopy(cost['process_hours']),
            quantity_retained=cid in quantity_body, quantity_dominated_by=excluded_body.get(cid, []),
            mechanics_retained=None, mechanics_evaluation_id=None,
            structural_status='not-run; full-body evaluator unavailable for these topologies',
            model_deflection_upper_m=None, complete_installed_mass_kg=None,
            next_tasks=['Develop topology-specific shell, laminate and joint evaluation',
                'Locate equipment, joints and fasteners; reconcile complete installed mass',
                'Validate production routes, fire, fatigue, clearances and repair access'],
            assumptions=dict(cost_basis=cost['basis'], cost_scope=cost['scope'],
                assumption_id=cost['assumption_id'],
                interface_screen=dict(status=screen['status'],
                    declared_functions_preserved=screen['declared_functions_preserved'],
                    issue_counts=[dict(code=code, status=status, count=count)
                        for (code, status), count in sorted(issues.items())])),
            **FLAGS))

    civil_rows = []
    for cid, row in civils.items():
        mech = mechanical[cid]
        cost = row['cost_estimate']
        if cost['candidate_id'] != cid or row['quantities']['candidate_id'] != cid:
            raise CurrentUnavailable('Civil cost or quantity candidate identity differs')
        lift_cases = mech['lifting']['cases']
        if (mech['lifting']['candidate_id'] != cid
                or [case['name'] for case in lift_cases] != ['low', 'base', 'high']):
            raise CurrentUnavailable('Civil lifting candidate or scenario coverage differs')
        civil_rows.append(dict(candidate_id=cid, definition_id=None,
            quantity_record_sha256=identity(row), quantity_evaluation_id=row['evaluation_id'],
            descriptor=deepcopy(row['descriptor']), profile=row['profile'],
            stock_mass_kg=row['metrics']['nominal_stock_mass_kg'],
            cost_iqd={case['name']: case['lift_adjusted_scoped_installed_iqd'] for case in lift_cases},
            process_hours=deepcopy(cost['factory_person_hours']),
            quantity_retained=cid in quantity_civil, quantity_dominated_by=excluded_civil.get(cid, []),
            mechanics_retained=cid in mechanical_retained, mechanics_evaluation_id=mech['evaluation_id'],
            structural_status='partial beam calculations exist; stage 1 incomplete; stage 2 not admitted',
            model_deflection_upper_m=mech['metrics']['crowd_high_mass_model_deflection_upper_m'],
            complete_installed_mass_kg=None, next_tasks=deepcopy(mech['next_tasks']),
            assumptions=dict(cost_basis=cost['quantity_basis'],
                elastic_hypothesis=mech['primary_elastic_hypothesis'],
                deflection_scope='Crowd/high accounted-mass model bound; unvalidated gross-elastic material/load-transfer hypotheses. No physical bound or acceptance limit.',
                lifting=deepcopy(mech['lifting']), load_context_id=context['context_id'],
                quantity_assumption_id=cost['assumption_id'],
                mechanical_case_evaluation_ids=deepcopy(mech['case_evaluation_ids'])), **FLAGS))

    portfolios = [dict(key='body', label='17 m carbody stock',
        portfolio_id=body['portfolio_id'], quantity_archive_id=body['archive']['archive_id'],
        mechanics_archive_id=None, quantity_retained_count=len(quantity_body), mechanics_retained_count=None,
        unit='one 17 m car body; nominal stock only',
        process_hours_label='Factory process-hours',
        cost_scope='Class C factory-gate body stock per car. Excludes equipped vehicle, joints/fasteners, delivery, installation and lifecycle costs.',
        assumptions={key: deepcopy(body['specification'][key]) for key in
            ('production_basis', 'civil_basis', 'operations_scenarios', 'unsupported_families')},
        evidence_path='/docs/design-engine/breadth-first-shape-portfolio/README.md',
        geometry_path='/docs/design-engine/breadth-first-shape-portfolio/candidates.json.gz',
        rows=body_rows),
        dict(key='civil', label='20 m civil spans', portfolio_id=civil['portfolio_id'],
            quantity_archive_id=civil['archive']['archive_id'],
            mechanics_archive_id=mechanics['archive']['archive_id'],
            quantity_retained_count=len(quantity_civil), mechanics_retained_count=len(mechanical_retained),
            unit='one nominal 20 m span with the common 2 m deck envelope',
            process_hours_label='Factory person-hours',
            cost_scope='Class C scoped installed span estimate with lifting adjustment. Includes declared rail/support/foundation reserves; complete installed cost remains unknown.',
            assumptions=dict(production=civil['specification']['production'],
                construction=civil['specification']['construction'],
                mechanical_specification=deepcopy(mechanics['specification']),
                load_context=deepcopy(context), geometry_scope=civil['geometry_scope']),
            evidence_path='/docs/design-engine/civil-shape-mechanics/README.md',
            geometry_path='/docs/design-engine/civil-shape-portfolio/sections.svg',
            rows=civil_rows)]
    if topology is not None:
        portfolios.append(_topology(topology, baseline))
    if topology_revisions is not None:
        if topology is None or topology_parent_binding is None:raise CurrentUnavailable('Revision portfolio requires authenticated parent publication')
        portfolios.append(_topology_revisions(topology_revisions,topology,baseline,topology_parent_binding))
    for portfolio in portfolios:
        portfolio['rows'].sort(key=lambda row: row['candidate_id'])
        portfolio['candidate_count'] = len(portfolio['rows'])
    return dict(schema='osr-design-portfolio-view/1',
        selected_reference_context=dict(selection_id=baseline['selection_id'], candidate_id=vehicle['candidate_id']),
        portfolios=portfolios, numerical_jobs_dispatched=0, integrated_selection=None, **FLAGS)


def read(root, publication, baseline):
    body = _read(root, publication, 'breadth-first-shape-portfolio', 'result.json',
        'osr-breadth-first-shape-portfolio/1', 'portfolio_id')
    civil = _read(root, publication, 'civil-shape-portfolio', 'result.json',
        'osr-civil-shape-portfolio/1', 'portfolio_id')
    mechanics = _read(root, publication, 'civil-shape-mechanics', 'result.json.gz',
        'osr-civil-shape-mechanics/1', 'study_id')
    topology = _read(root, publication, 'civil-topology', 'result.json',
        'osr-civil-topology-portfolio/1', 'portfolio_id')
    parent_manifest = _read(root, publication, 'civil-topology', 'manifest.json',
        'osr-civil-topology-publication/1', 'manifest_id')
    if (parent_manifest['portfolio_id']!=topology['portfolio_id']
            or parent_manifest['files_sha256']['result.json']!=publication['source_sha256']['docs/design-engine/civil-topology/result.json']):
        raise CurrentUnavailable('Revision parent publication/result binding differs')
    revisions = _read(root, publication, 'civil-topology-revisions', 'result.json',
        'osr-topology-revision-portfolio/1', 'portfolio_id')
    binding=dict(path='docs/design-engine/civil-topology',manifest_id=parent_manifest['manifest_id'],
        manifest_sha256=publication['source_sha256']['docs/design-engine/civil-topology/manifest.json'],
        state_sha256=parent_manifest['files_sha256']['state.json'],campaign_id=topology['campaign_id'],
        files_sha256=parent_manifest['files_sha256'])
    return project(body, civil, mechanics, baseline, topology, revisions, binding)


def _finite(value):
    try:return type(value) in (int,float) and isfinite(value) and value>=0
    except OverflowError:return False


def _topology_revisions(record,parent_record,baseline,parent_binding):
    _sealed(record,'portfolio_id');_research(record);_sealed(parent_record,'portfolio_id');_research(parent_record)
    binding={k:v for k,v in parent_binding.items() if k!='files_sha256'}
    if (record['parent_publication']!=binding or binding['campaign_id']!=parent_record['campaign_id']
            or record['selection_id']!=baseline['selection_id'] or record['selected_vehicle_candidate_id']!=baseline['vehicle']['candidate_id']
            or record['vehicle_evaluation_id']!=baseline['vehicle']['evaluation_id']
            or any(record[key]!=parent_record[key] for key in ('baseline_id','load_context_id','selection_id','selected_vehicle_candidate_id','vehicle_evaluation_id'))
            or record['physical_model_or_material_strength_qualified'] is not False
            or record['current_evaluator_admission'] is not False):
        raise CurrentUnavailable('Revision parent publication or selected candidate/evaluation/load identity differs')
    originals={a['trial_id']:a for a in parent_record['attempts']};realized={};eligible={};evaluations=set();trials=set();attempts=[]
    scopes={'rolling-stock','guideway','stations-power','factory-tooling','construction','land-utilities-depot','fleet','energy','operations','maintenance','renewals','recovery','reliability','disposal'}
    def sha(value):return isinstance(value,str) and re.fullmatch('[a-f0-9]{64}',value) is not None
    for attempt in record['attempts']:
        _research(attempt)
        if (any(not sha(attempt[key]) for key in ('trial_id','request_id','attempt_id')) or attempt['trial_id'] in trials
                or attempt['physical_model_or_material_strength_qualified'] is not False or attempt['current_evaluator_admission'] is not False):
            raise CurrentUnavailable('Revision attempt identity/disposition differs')
        trials.add(attempt['trial_id']);old=originals.get(attempt['parent_trial_id'])
        if (old is None or any(attempt['parent_'+key]!=old[key] for key in ('request_id','evaluation_id','candidate_id'))
                or attempt['parent_arrays_package_sha256']!=parent_binding['files_sha256'].get('trials/'+attempt['parent_trial_id']+'/arrays.npz')):
            raise CurrentUnavailable('Revision original parent request/evaluation/geometry/arrays differ')
        attempts.append({k:deepcopy(attempt.get(k)) for k in ('trial_id','request_id','attempt_id','parent_trial_id','parent_evaluation_id','candidate_id',
            'evaluation_id','execution','proposal_execution','strategy','refinement_status','coarse_replay','fine_replay','binary_replay_admitted_to_archive','failure_reason')})
        cid=attempt['candidate_id']
        if cid is None:
            if attempt['binary_replay_admitted_to_archive']:raise CurrentUnavailable('Unrealized revision cannot enter archive')
            continue
        if (not sha(cid) or not sha(attempt['evaluation_id']) or attempt['evaluation_id'] in evaluations
                or not sha(attempt['quantity_evaluation_id']) or not sha(attempt['composition_candidate_id'])
                or not sha(attempt['revision_id'])
                or not _finite(attempt['nominal_stock_mass_kg']) or set(attempt['span_installed_cost_iqd'])!={'low','base','high'}
                or any(not _finite(v) for v in attempt['span_installed_cost_iqd'].values())
                or not isinstance(attempt.get('factory_person_hours'),dict)
                or set(attempt['factory_person_hours'])!={'low','base','high'}
                or any(not _finite(v) for v in attempt['factory_person_hours'].values())):
            raise CurrentUnavailable('Revision physical/evaluation identity, mass, scoped costs or factory hours differ')
        evaluations.add(attempt['evaluation_id']);costs=attempt['span_installed_cost_iqd']
        if not costs['low']<=costs['base']<=costs['high']:raise CurrentUnavailable('Revision scoped cost cases differ')
        whole=attempt['system_cost']
        if not sha(whole['evaluation_id']) or set(whole['cases'])!={'low','base','high'}:raise CurrentUnavailable('Revision whole-system cost axes differ')
        for case in whole['cases'].values():
            if set(case['scope_totals_iqd'])!=scopes:raise CurrentUnavailable('Revision whole-system scope coverage differs')
            triples=[case[k] for k in ('factory_gate_cost_iqd','delivered_cost_iqd','model_based_installed_CAPEX_iqd','model_based_whole_life_NPV_iqd')]+list(case['scope_totals_iqd'].values())
            if any(not isinstance(v,list) or len(v)!=3 or any(not _finite(x) for x in v) for v in triples):raise CurrentUnavailable('Finite complete revision cost triples required')
        valid=True
        for name in ('coarse_replay','fine_replay'):
            replay=attempt[name]
            if replay['execution']=='completed':
                if replay['case_count']!=81 or not _finite(replay['maximum_vertical_displacement_m']):raise CurrentUnavailable('Revision 81-case numerical summary differs')
            valid=valid and replay['execution']=='completed' and replay['residual_request_met'] is True
        if attempt['binary_replay_admitted_to_archive'] is not valid:raise CurrentUnavailable('Revision residual/archive eligibility differs')
        if cid in realized and realized[cid]['composition_candidate_id']!=attempt['composition_candidate_id']:raise CurrentUnavailable('Same revision geometry has mixed system candidate identity')
        preference=lambda a:(not a['binary_replay_admitted_to_archive'],a['evaluation_id'])
        if cid not in realized or preference(attempt)<preference(realized[cid]):realized[cid]=attempt
        if valid:eligible[cid]=attempt
    retained,excluded=_archive(dict(archive=record['archive']),eligible)
    if (len(trials)!=record['trial_count'] or len(realized)!=record['unique_realized_candidate_count']
            or len(eligible)!=record['archive_eligible_candidate_count']
            or sum(a['binary_replay_admitted_to_archive'] for a in record['attempts'])!=record['archive_eligible_attempt_count']
            or sum(any(a[n] is not None and a[n]['execution']=='completed' and not a[n]['residual_request_met'] for n in ('coarse_replay','fine_replay')) for a in record['attempts'])!=record['residual_gate_failed_attempt_count']
            or sum(a['refinement_status']=='mesh-unresolved' for a in record['attempts'])!=record['mesh_unresolved_attempt_count']):
        raise CurrentUnavailable('Revision attempt/realized/eligible coverage differs')
    rows=[]
    for cid,a in realized.items():
        fine=a['fine_replay'];valid=cid in eligible
        rows.append(dict(candidate_id=cid,definition_id=None,quantity_record_sha256=identity(a),quantity_evaluation_id=a['quantity_evaluation_id'],
            descriptor=dict(material='steel-concrete',manufacture='cut-plate-and-precast-deck',revision_strategy=a['strategy']),profile=a['strategy'],
            stock_mass_kg=a['nominal_stock_mass_kg'],cost_iqd=deepcopy(a['span_installed_cost_iqd']),process_hours=deepcopy(a['factory_person_hours']),
            quantity_retained=None,quantity_dominated_by=[],
            mechanics_retained=cid in retained if valid else None,mechanics_evaluation_id=a['evaluation_id'],
            structural_status=('declared numerical residual request met' if valid else 'declared numerical residual request NOT met')+'; '+a['refinement_status']+'; physical model and strength unqualified',
            model_deflection_upper_m=fine['maximum_vertical_displacement_m'] if fine['execution']=='completed' else None,
            complete_installed_mass_kg=None,next_tasks=['Resolve mesh sensitivity and large-displacement model validity','Establish 3D torsion, unequal web sharing and bearing contact','Validate material strength, buckling, fatigue, connections and manufacturing'],
            assumptions=dict(trial_record_path='/docs/design-engine/civil-topology-revisions/trials/'+a['trial_id']+'/result.json.gz',
                parent_trial_id=a['parent_trial_id'],parent_evaluation_id=a['parent_evaluation_id'],revision_id=a['revision_id'],
                baseline_id=record['baseline_id'],load_context_id=record['load_context_id'],composition_candidate_id=a['composition_candidate_id'],
                whole_system_cost=deepcopy(a['system_cost']),coarse_replay=deepcopy(a['coarse_replay']),fine_replay=deepcopy(fine),
                compliance_relative_changes=deepcopy(a['compliance_relative_changes']),archive_exclusion=excluded.get(cid,[]),
                deflection_scope='Maximum over 81 representative elastic plane-model cases; no all-position or physical upper bound; large displacement may invalidate the model'),**FLAGS))
    return dict(key='topology-revisions',label='20 m explicit web revisions',portfolio_id=record['portfolio_id'],
        quantity_archive_id=None,mechanics_archive_id=record['archive']['archive_id'],quantity_retained_count=None,mechanics_retained_count=len(retained),
        unit='One paired-web/deck span; explicit physical revisions, unqualified 2D research model',process_hours_label='Factory person-hours',
        deflection_label='Maximum recorded model displacement across 81 representative cases',
        cost_scope='Class C scoped installed span; full fourteen-scope same-service costs remain separate in assumptions.',
        assumptions=dict(parent_publication=deepcopy(record['parent_publication']),ranking_scope=record['ranking_scope'],
            terminal_attempt_count=record['trial_count'],archive_eligible_attempt_count=record['archive_eligible_attempt_count'],
            residual_gate_failed_attempt_count=record['residual_gate_failed_attempt_count'],mesh_unresolved_attempt_count=record['mesh_unresolved_attempt_count'],attempts=attempts),
        evidence_path='/docs/design-engine/civil-topology-revisions/result.json',geometry_path='/docs/design-engine/civil-topology-revisions/revisions.svg',rows=rows)


def _topology(record, baseline):
    _sealed(record, 'portfolio_id'); _research(record)
    if (record['selection_id'] != baseline['selection_id']
            or record['selected_vehicle_candidate_id'] != baseline['vehicle']['candidate_id']
            or record['vehicle_evaluation_id'] != baseline['vehicle']['evaluation_id']):
        raise CurrentUnavailable('Topology selected vehicle/load context differs')
    realized = {}
    eligible = {}
    for attempt in record['attempts']:
        _research(attempt)
        cid = attempt['candidate_id']
        if cid is not None:
            realized.setdefault(cid, attempt)
            if attempt['binary_replay_admitted_to_archive']:
                eligible[cid] = attempt
    realized.update(eligible)
    retained, exclusions = _archive(dict(archive=record['archive']), eligible)
    if len(realized) != record['unique_realized_candidate_count'] or len(eligible) != record['numerically_replayed_candidate_count']:
        raise CurrentUnavailable('Topology realized/eligible candidate coverage differs')
    rows = []
    for cid, attempt in realized.items():
        trial = attempt['trial']
        rows.append(dict(candidate_id=cid, definition_id=None,
            quantity_record_sha256=identity(attempt), quantity_evaluation_id=attempt['quantity_evaluation_id'],
            descriptor=dict(material='steel-concrete', manufacture='cut-plate-and-precast-deck',
                initial_field=trial['initial_field'], target_solid_fraction=trial['volume_fraction']),
            profile=trial['kind'], stock_mass_kg=attempt['nominal_stock_mass_kg'],
            cost_iqd=deepcopy(attempt['span_installed_cost_iqd']), process_hours=deepcopy(attempt['factory_person_hours']),
            quantity_retained=None, quantity_dominated_by=[],
            mechanics_retained=(cid in retained if cid in eligible else None),
            mechanics_evaluation_id=attempt['evaluation_id'],
            structural_status=attempt['binary_replay']+'; '+str(attempt.get('binary_failure_reason') or attempt['refinement_status'])+'; plane-model research only',
            model_deflection_upper_m=attempt['maximum_crowd_high_accounted_mass_model_displacement_m'],
            complete_installed_mass_kg=None, next_tasks=deepcopy(record['physical_qualification_pending']),
            assumptions=dict(scope='Per-span scoped installed costs exclude rails, foundations and full corridor plant; whole-corridor cost comparisons below retain all fourteen scopes',
                deflection_scope='Representative crowd/high vehicle and span mass positions only; no all-position or physical upper bound',
                composition_candidate_id=attempt['composition_candidate_id'],
                whole_system_cost=deepcopy(attempt['system_cost']),
                load_context_id=record['load_context_id'], baseline_id=record['baseline_id'],
                numerical_archive_eligible=cid in eligible, archive_exclusion=exclusions.get(cid, [])), **FLAGS))
    return dict(key='topology', label='20 m generated web topologies', portfolio_id=record['portfolio_id'],
        quantity_archive_id=None, mechanics_archive_id=record['archive']['archive_id'],
        quantity_retained_count=None, mechanics_retained_count=len(retained),
        unit='One nominal twin-web/deck span; two-dimensional research model',
        process_hours_label='Factory person-hours',
        deflection_label='Representative crowd/high-mass model displacement',
        cost_scope='Class C scoped installed plate/deck span; rails, site foundations and corridor plant shown separately in whole-system assumptions.',
        assumptions=dict(ranking_scope=record['ranking_scope'],
            archive_objectives=record['archive']['objectives'], failed_attempt_count=sum(row['candidate_id'] is None for row in record['attempts']),
            physical_qualification_pending=deepcopy(record['physical_qualification_pending'])),
        evidence_path='/docs/design-engine/civil-topology/README.md',
        geometry_path='/docs/design-engine/civil-topology/topologies.svg', rows=rows)
