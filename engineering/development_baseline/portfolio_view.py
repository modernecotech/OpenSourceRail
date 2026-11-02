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


def project(body, civil, mechanics, baseline):
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
    return project(body, civil, mechanics, baseline)
