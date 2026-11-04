"""Progressive outline acceptance for comparison and further design.

Bounded assumptions can complete an outline. This policy does not authenticate
physical evidence, approve an operating map, or replace the existing human and
qualification workflows. An unsupported model verdict is an evidence task.
"""
from copy import deepcopy
from math import isfinite
from pathlib import Path
import json

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.design_search import requirement_policy

PRODUCER = 'engineering/outline/maturity.py'
STAGES = ('outline', 'concept', 'detail', 'prototype', 'release')
STATUSES = ('pass', 'fail', 'unknown', 'out-of-domain')
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False,
    native_evaluator_admission=False, available_force_map_admitted=False,
    selected_reference_changed=False, installed_mass_complete=False)
RELEASE_CLAIMS = (*FLAGS, 'physical_qualified', 'manufacturing_approved',
    'operation_approved', 'safety_approved', 'actual_force_map_supported')


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _json(value):
    """Require finite JSON data; dictionary keys are explicit strings."""
    if value is None or type(value) in (str, bool): return
    if type(value) in (int, float):
        if not isfinite(value): raise ValueError('Nonfinite outline input')
        return
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value): raise ValueError('String JSON keys required')
        for child in value.values(): _json(child)
        return
    if isinstance(value, list):
        for child in value: _json(child)
        return
    raise ValueError('JSON-only outline inputs required')


def _bounds(value, *, positive=False, complete=True):
    """Validate numeric intervals; unknown values stay unknown, never zero."""
    if value is None: return None
    if not isinstance(value, dict): raise ValueError('Explicit numeric bound mapping required')
    keys = ('low', 'base', 'high')
    known = [(i, value.get(key)) for i, key in enumerate(keys) if value.get(key) is not None]
    for _, number in known:
        if type(number) not in (int, float) or not isfinite(number):
            raise ValueError('Finite numeric bounds required')
        if positive and number <= 0: raise ValueError('Positive outline mass/cost bounds required')
    if any(a > b for (_, a), (_, b) in zip(known, known[1:])):
        raise ValueError('Bounds must satisfy low <= base <= high')
    if len(known) != 3: return None if complete else value
    return {key:value[key] for key in keys}


def _assumptions(rows):
    if rows is None: rows = []
    if not isinstance(rows, list): raise ValueError('Explicit assumption list required')
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not _text(row.get('id')) or row['id'] in result:
            raise ValueError('Unique explicit assumption IDs required')
        if not _text(row.get('purpose')) or not (_text(row.get('source')) or isinstance(row.get('source'), dict) and bool(row['source'])):
            raise ValueError('Assumptions require source and purpose')
        bounds = row.get('bounds')
        if isinstance(bounds, dict) and any(key in bounds for key in ('low', 'base', 'high')):
            if _bounds(bounds) is None: raise ValueError('Complete bounded assumption required')
        elif isinstance(bounds, list) and len(bounds) in (2, 3):
            if any(type(x) not in (int, float) or not isfinite(x) for x in bounds) or bounds != sorted(bounds):
                raise ValueError('Ordered finite assumption interval required')
        elif isinstance(bounds, dict) and set(bounds) == {'choices'}:
            if not isinstance(bounds['choices'], list) or not bounds['choices'] or any(not _text(x) for x in bounds['choices']):
                raise ValueError('Nonempty explicit bounded choices required')
        else: raise ValueError('Explicit numeric or discrete assumption bounds required')
        result[row['id']] = deepcopy(row)
    return result


def _resolved_bounds(value, assumptions, *, positive):
    if value is None: return None, None
    if not isinstance(value, dict): raise ValueError('Bounded quantity record required')
    assumed = value.get('assumption_id')
    own = _bounds(value, positive=positive)
    if own is not None: return own, assumed
    if assumed in assumptions:
        bounds = assumptions[assumed]['bounds']
        if isinstance(bounds, dict): return _bounds(bounds, positive=positive), assumed
    return None, assumed


def _dimensions(envelope):
    if not isinstance(envelope, dict): raise ValueError('Envelope records required')
    sizes = envelope.get('dimensions_m')
    if sizes is None and all(k in envelope for k in ('length_m', 'width_m', 'height_m')):
        sizes = [envelope[k] for k in ('length_m', 'width_m', 'height_m')]
    if sizes is None: return None
    if not isinstance(sizes, list) or len(sizes) != 3:
        raise ValueError('Three explicit envelope dimensions required')
    if any(type(x) not in (int, float) or not isfinite(x) or x <= 0 for x in sizes):
        raise ValueError('Positive finite envelope dimensions required')
    return sizes


def assess(record, *, root=ROOT):
    """Accept coherent outlines positively while keeping later maturity separate.

    A constraint's ``known_physical_contradiction`` is an upstream declared fact,
    not authenticated by this module. Model-domain failures cannot set that flag.
    A valid assumption resolves an outline study condition only; it never becomes
    an available-force map, tested assembly, supplier quote or physical approval.
    """
    if not isinstance(record, dict): raise ValueError('Outline record mapping required')
    _json(record); value = deepcopy(record); root = Path(root)
    if digest(root/PRODUCER) != digest(__file__): raise ValueError('Executing outline policy differs from source root')
    for key in ('outline_id', 'requirements_id'):
        if not _text(value.get(key)): raise ValueError('Explicit '+key+' required')
    assumptions = _assumptions(value.get('assumptions', []))
    tasks = []; missing = []; contradictions = []; findings = []
    def task(key, phase, kind, explanation, *, blocking=False):
        row = dict(key=key, phase=phase, kind=kind, explanation=explanation,
            blocks_outline=blocking, outline_id=value['outline_id'], requirements_id=value['requirements_id'])
        row['task_id'] = identity(row); tasks.append(row)
    def definition(key, explanation):
        missing.append(dict(key=key, reason=explanation)); task(key, 'outline', 'define-bounded-input', explanation, blocking=True)
    envelopes = value.get('envelopes')
    if not isinstance(envelopes, list) or not envelopes:
        definition('envelopes', 'Define finite physical envelopes for the outline.')
    else:
        for i, envelope in enumerate(envelopes):
            if _dimensions(envelope) is None:
                definition('envelope/'+str(i), 'Specify a positive three-dimensional envelope; detailed CAD can follow later.')
            if envelope.get('assumption_id') is not None and envelope['assumption_id'] not in assumptions:
                definition('envelope/'+str(i)+'.assumption_id', 'Resolve the declared bounded envelope assumption.')
    mass, mass_assumption = _resolved_bounds(value.get('bounded_mass_kg'), assumptions, positive=True)
    if mass is None: definition('bounded_mass_kg', 'Provide calculated or explicitly assumed low/base/high mass bounds.')
    cost_value = value.get('costs'); cost, cost_assumption = _resolved_bounds(cost_value, assumptions, positive=True)
    if cost is None: definition('costs', 'Provide provisional low/base/high costs rather than replacing unknown cost with zero.')
    if not isinstance(cost_value, dict) or not _text(cost_value.get('currency')) or not _text(cost_value.get('source_class')):
        definition('costs.provenance', 'Declare cost currency and evidence class; Class C engineering estimates are permitted.')
    for key, assumption_id in (('bounded_mass_kg', mass_assumption), ('costs', cost_assumption)):
        if assumption_id is not None and assumption_id not in assumptions:
            definition(key+'.assumption_id', 'Resolve the declared bounded assumption ID.')
    routes = value.get('manufacturing_routes')
    if not isinstance(routes, list) or not routes:
        definition('manufacturing_routes', 'Assign provisional production or purchasing routes; released manufacturing detail is a later stage.')
    elif any(not (_text(row) or isinstance(row, dict) and bool(row)) for row in routes):
        raise ValueError('Nonempty provisional route records required')
    constraints = value.get('service_constraints')
    if not isinstance(constraints, list): constraints = []
    if not constraints or not any(isinstance(row, dict) and row.get('required_at') == 'outline' for row in constraints):
        definition('outline.functional_requirements', 'Declare the functional requirements that must be satisfied at outline stage.')
    seen = set()
    for row in constraints:
        if not isinstance(row, dict) or not _text(row.get('key')) or row['key'] in seen:
            raise ValueError('Unique named constraint records required')
        seen.add(row['key']); status = row.get('status'); phase = row.get('required_at')
        for binding in ('outline_id', 'requirements_id'):
            if row.get(binding) is not None and row[binding] != value[binding]:
                raise ValueError('Mixed outline/requirement identity in constraint')
        known = row.get('known_physical_contradiction', False)
        if status not in STATUSES or phase not in STAGES or type(known) is not bool or not _text(row.get('explanation')):
            raise ValueError('Typed constraint status, phase, contradiction and explanation required')
        if known and status != 'fail': raise ValueError('Only a supported failed physical constraint can declare a contradiction')
        aid = row.get('assumption_id'); bounded = aid in assumptions if aid is not None else False
        synthetic = row.get('synthetic') is True or row.get('evidence_kind') in ('synthetic', 'synthetic-map', 'assumed-map')
        if aid is not None and not bounded:
            if phase == 'outline': definition(row['key']+'.assumption_id', 'Resolve the named bounded study assumption.')
            else: task(row['key']+'.assumption_id', phase, 'define-bounded-input', 'Resolve the named assumption before the later-stage evaluation.')
        if known:
            contradictions.append(dict(key=row['key'], reason=row['explanation']))
            task(row['key'], 'outline', 'revise-outline', row['explanation'], blocking=True)
            disposition = 'known-physical-contradiction'
        elif phase == 'outline' and (status != 'pass' or synthetic) and not bounded:
            definition(row['key'], 'Define a bounded study assumption or an appropriate outline evaluator: '+row['explanation'])
            disposition = 'needs-definition'
        elif phase == 'outline':
            disposition = 'conditionally-satisfied' if bounded else 'satisfied-for-outline'
            if status != 'pass' or synthetic:
                task(row['key'], 'concept', 'evaluate-assumption', row['explanation'])
        else:
            disposition = 'later-stage-task' if status != 'pass' else 'reported-later-stage-result'
            if status != 'pass' or bounded or synthetic:
                task(row['key'], phase, 'extend-evaluator' if status == 'out-of-domain' else 'complete-later-stage-evidence', row['explanation'])
        findings.append(dict(key=row['key'], required_at=phase, reported_status=status,
            disposition=disposition, assumption_id=aid, bounded_assumption=bounded,
            known_physical_contradiction=known, synthetic_is_physical_evidence=False,
            physical_failure_inferred=known))
    blocked = sorted(key for key in RELEASE_CLAIMS if value.get(key) is True)
    if blocked:
        task('release-claims', 'release', 'existing-qualification-review',
            'Input claims cannot grant qualification or release; use authenticated records and independent human review in the existing workflow.')
    accepted = not missing and not contradictions
    decision = 'needs-revision' if contradictions else 'needs-definition' if missing else 'accepted'
    result = dict(schema='osr-progressive-outline-maturity/1', policy_revision='OUTLINE-MATURITY-1',
        outline_id=value['outline_id'], requirements_id=value['requirements_id'], input_record_id=identity(value),
        execution='completed', execution_scope='outline-policy-assessment-only',
        reported_execution=value.get('execution'), reported_numerical_validity=value.get('numerical_validity'),
        definition_validity='valid', numerical_validity='not-required-for-outline-acceptance',
        outline_acceptance=decision, outline_accepted=accepted,
        comparison_admitted=accepted, detailing_admitted=accepted,
        acceptance_purpose='Comparison and progressive design development using visible bounded assumptions.',
        requirement_coverage='Supplied named requirements; the coordinator binds their complete required set.',
        concept_screen='not-assessed', detailed_design='not-assessed', prototype_validation='not-assessed',
        manufacturing_authorisation='existing-qualification-workflow-required', operation_authorisation='existing-qualification-workflow-required',
        resolved_mass_bounds_kg=mass, resolved_cost_bounds=cost, cost_currency=cost_value.get('currency') if isinstance(cost_value, dict) else None,
        assumption_ids=sorted(assumptions), findings=findings, reasons=[*contradictions, *missing],
        next_tasks=tasks, blocked_release_claims=blocked, physical_acceptance_inferred=False,
        requirement_policy_id=requirement_policy.catalogue()['policy_id'],
        qualification_authority=dict(workflow='engineering.railway_completion.evidence',
            rule='Existing external authentication, approved procedures/limits and independent review remain the only physical-evidence route; this policy issues no such decision.'),
        source_sha256={name:digest(root/name) for name in (PRODUCER, requirement_policy.PRODUCER,
            'engineering/station_rail/common.py', 'engineering/railway_completion/evidence.py')}, **FLAGS)
    result['evaluation_id'] = identity(result)
    return result
