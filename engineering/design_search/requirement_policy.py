"""Requirement policy for research screening, never physical qualification.

A provisional target is not a physical failure limit. Numerical-model admission
bounds are not material strengths. Referenced evidence/review identities below
must be authenticated by the existing qualification workflow; this pure module
checks their declared scope and never issues a release or rewrites old results.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite
from pathlib import Path
import json
import re
from typing import Literal, TypedDict

Category=Literal['mandatory_obligation','project_preference','revisable_assumption','numerical_validity_domain']
CATEGORIES=('mandatory_obligation','project_preference','revisable_assumption','numerical_validity_domain')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False,selected_development_default_changed=False)
PRODUCER='engineering/design_search/requirement_policy.py'


class Criterion(TypedDict):
    id:str
    category:Category
    obligation_kind:str|None
    observable:str
    unit:str
    operator:str
    limit:float|None
    provenance:dict|None
    affected_interfaces:list[str]


def identity(value):return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()

def _sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None

def _number(value):return type(value) in (float,int) and isfinite(value)


def _criterion(uid,category,observable,unit,operator,limit=None,*,kind=None,interfaces=(),model_id=None):
    return dict(id=uid,category=category,obligation_kind=kind,observable=observable,unit=unit,operator=operator,limit=limit,
        provenance=None,affected_interfaces=list(interfaces),model_id=model_id,
        acceptance_status='unassigned' if category=='mandatory_obligation' else 'not-an-acceptance-limit',**FLAGS)


def catalogue():
    rows=[
      _criterion('functional.integrated_service','mandatory_obligation','protected_service_demonstrated','1','verified',kind='functional',interfaces=('vehicle','station','route','controls','recovery')),
      _criterion('safety.structural_integrity','mandatory_obligation','strength_stability_fatigue_supported','1','verified',kind='physical-and-safety',interfaces=('body','joints','bogies','civil','crowd-loads')),
      _criterion('safety.independent_stop','mandatory_obligation','independent_stopping_and_parking_supported','1','verified',kind='safety',interfaces=('brakes','adhesion','controls','faults','recovery')),
      _criterion('accessibility.boarding_egress','mandatory_obligation','accessible_boarding_and_egress_supported','1','verified',kind='accessibility',interfaces=('doors','platform','wheelchair-routes','evacuation')),
      _criterion('physical.clearance','mandatory_obligation','maximum_interface_displacement_m','m','max',kind='physical-interface',interfaces=('structure','runninggear','motor-gap','doors','platform','thermal-movement')),
      _criterion('physical.temperature','mandatory_obligation','maximum_material_temperature_C','degC','max',kind='physical-material',interfaces=('material-lot','roof','HVAC','electrical','fire')),
      _criterion('target.global_deflection','project_preference','body_vertical_displacement_m','m','max',.0256,interfaces=('body','clearance','ride-response','doors','joints')),
      _criterion('target.whole_life_cost','project_preference','whole_life_cost_USD','USD','minimize',interfaces=('vehicle','guideway','stations','energy','renewals','service')),
      _criterion('assumption.speed_cap','revisable_assumption','speed_cap_m_s','m/s','max',20.,interfaces=('propulsion','brakes','ride-response','route','fleet','power')),
      _criterion('assumption.headway','revisable_assumption','headway_s','s','max',120.,interfaces=('capacity','dwell','receiving-berth','protection','fleet')),
      _criterion('model.linear_steel','numerical_validity_domain','maximum_linear_model_steel_B_T','T','max',1.3,model_id='linear-steel-mu1000/1',interfaces=('field-model','native-adapter','material-data','benchmark')),
    ]
    criteria={r['id']:r for r in rows}
    criteria['target.global_deflection'].update(
        basis='Retained L/500-style research comparison at25.6mm; provisional, not a universal body acceptance limit',
        derivation_required=['Actual motor/rail/door/platform clearance budgets','Static plus dynamic deformations and tolerances','Ride, stress, buckling, fatigue and function under applicable load cases'])
    criteria['model.linear_steel']['basis']='Conservative admission bound of the retained linear magnetic hypothesis, not a physical saturation or material-strength limit'
    result=dict(schema='osr-requirement-policy/1',revision='REQUIREMENT-POLICY-1',criteria=criteria,
        functional_obligations_are_nonnegotiable=True,quantitative_limits_require_derived_scope_and_evidence=True,
        historical_evaluations_are_immutable=True,unknown_is_zero=False,
        supported_basis_fields=['candidate_id','observable','unit','operator','limit','basis_kind','source_uri','source_locator','source_sha256','review_record_id','review_disposition'],
        example_references=[dict(uri='https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A32014R1302',
            sections=['4.2.2.4','4.2.2.7','4.2.2.10'],role='Example reference for engineering review only',
            applicability='unassessed; no Iraqi or urban-rail legal applicability or compliance claimed',
            raw_source_sha256=None,review_status='external reference; authenticated project basis not assigned')],
        source_sha256={PRODUCER:sha256(Path(__file__).read_bytes()).hexdigest()},**FLAGS)
    result['policy_id']=identity(result);return result


def _criteria(value,*,proposal=False):
    rows=deepcopy(catalogue()['criteria'] if value is None else value)
    if not isinstance(rows,dict):raise ValueError('Criterion mapping required')
    for uid,row in rows.items():
        if row.get('id')!=uid or row.get('category') not in CATEGORIES or not row.get('observable') or not row.get('unit'):raise ValueError('Typed criterion identity/category/observable/unit required')
        if row.get('operator') not in ('max','min','verified','minimize'):raise ValueError('Supported comparison operator required')
        if row.get('limit') is not None and not _number(row['limit']):raise ValueError('Finite limit or explicit unknown required')
        if not proposal and uid=='model.linear_steel' and row.get('model_id')=='linear-steel-mu1000/1' and (row['unit']!='T' or row['operator']!='max' or row['limit'] is None or row['limit']>1.3):
            raise ValueError('The retained1.3T linear-model domain cannot be enlarged by changing a limit')
    json.dumps(rows,allow_nan=False);return rows


def _basis_supported(criterion,candidate_id):
    p=criterion.get('provenance')
    return (isinstance(p,dict) and _sha(candidate_id) and p.get('candidate_id')==candidate_id
        and all(p.get(n)==criterion.get(n) for n in ('observable','unit','operator','limit'))
        and p.get('basis_kind') in ('approved-interface-limit','reviewed-material-bound','approved-functional-procedure')
        and p.get('review_disposition')=='supported-for-declared-scope'
        and _sha(p.get('source_sha256')) and _sha(p.get('review_record_id'))
        and bool(p.get('source_uri')) and bool(p.get('source_locator')))


def _measurement(value,criterion):
    if value is None:return dict(value=None,unit=criterion['unit'])
    if type(value) in (int,float,bool):return dict(value=value,unit=criterion['unit'])
    if not isinstance(value,dict):raise ValueError('Numeric/boolean observation or explicit measurement record required')
    return deepcopy(value)


def _supported(row,criterion,candidate_id,requirement_revision):
    sources=row.get('source_sha256')
    return (row.get('candidate_id')==candidate_id and _sha(candidate_id) and row.get('observable')==criterion['observable']
        and row.get('requirement_revision')==requirement_revision
        and row.get('execution')=='completed' and row.get('numerical_validity') in ('valid','converged','not-applicable')
        and row.get('model_domain')=='supported' and row.get('evidence_kind') in ('verified-simulation','correlated-measurement')
        and _sha(row.get('evidence_id')) and _sha(row.get('evaluation_id')) and _sha(row.get('independent_review_id'))
        and isinstance(sources,dict) and bool(sources) and all(_sha(h) for h in sources.values()))


def _comparison(criterion,row):
    value=row.get('value');operator=criterion['operator'];limit=criterion.get('limit')
    if row.get('unit')!=criterion['unit']:return None,'unit-mismatch'
    if operator=='verified':return (value if type(value) is bool else None),'explicit-functional-procedure-required'
    if not _number(value):return None,'quantity-unknown'
    if operator=='minimize' or limit is None:return None,'limit-unassigned'
    return (value<=limit if operator=='max' else value>=limit),'numeric-comparison'


def assess(measurements,criteria=None,*,candidate_id=None,requirement_revision=None):
    """Assess targets and declared screens without asserting integrated acceptance.

    Bare values may describe advisory comparisons. Hard screens additionally
    require a scope-bound criterion basis and completed, reviewed, domain-valid
    evidence. Evidence IDs are references, not authenticated by this module.
    """
    if not isinstance(measurements,dict):raise ValueError('Measurement mapping required')
    if candidate_id is not None and not _sha(candidate_id):raise ValueError('Explicit physical candidate SHA required')
    rows=_criteria(criteria);revision=requirement_revision or identity(rows)
    if not isinstance(revision,str) or not revision:raise ValueError('Separate requirement revision required')
    json.dumps(measurements,allow_nan=False);findings=[]
    for uid,criterion in rows.items():
        if uid in measurements and criterion['observable'] in measurements and measurements[uid]!=measurements[criterion['observable']]:raise ValueError('Conflicting observable records')
        row=_measurement(measurements.get(uid,measurements.get(criterion['observable'])),criterion)
        for key,expected in (('candidate_id',candidate_id),('requirement_revision',revision)):
            if row.get(key) is not None and expected is not None and row[key]!=expected:raise ValueError('Mixed physical/requirement identity in observation')
        comparison,reason=_comparison(criterion,row);category=criterion['category'];support=_supported(row,criterion,candidate_id,revision)
        status='unknown';hard=False
        if category=='mandatory_obligation':
            if comparison is not None and support and _basis_supported(criterion,candidate_id):status='supported_screen_satisfied' if comparison else 'supported_limit_violated';hard=not comparison
            else:reason='Missing supported evidence or derived approved criterion basis; '+reason
        elif category=='project_preference':status='target_met' if comparison is True else 'target_exceeded' if comparison is False else 'unknown'
        elif category=='revisable_assumption':status='within_assumed_target' if comparison is True else 'assumption_challenged' if comparison is False else 'unknown'
        else:status='within_declared_model_bound' if comparison is True else 'outside_model_domain' if comparison is False else 'unknown'
        findings.append(dict(criterion_id=uid,category=category,observable=criterion['observable'],value=row.get('value'),unit=row.get('unit'),
            operator=criterion['operator'],limit=criterion.get('limit'),status=status,hard_screen_failed=hard,
            evidence_support='declared-reviewed-source-bound' if support else 'unknown-or-unsupported',reason=reason,
            affected_interfaces=criterion.get('affected_interfaces',[]),**FLAGS))
    mandatory=[r for r in findings if r['category']=='mandatory_obligation'];violated=any(r['hard_screen_failed'] for r in mandatory)
    mandatory_ids={k for k,v in catalogue()['criteria'].items() if v['category']=='mandatory_obligation'}
    omitted=sorted(mandatory_ids-set(rows))
    screen='fail' if violated else 'pass' if mandatory and not omitted and all(r['status']=='supported_screen_satisfied' for r in mandatory) else 'unknown'
    result=dict(schema='osr-requirement-assessment/1',candidate_id=candidate_id,requirement_revision=revision,
        policy_id=catalogue()['policy_id'],criteria_id=identity(rows),findings=findings,omitted_mandatory_obligations=omitted,
        declared_hard_screen=screen,integrated_suitability='incompatible_with_declared_supported_limit' if violated else 'unknown',
        integrated_qualification_required=True,evidence_authentication='External qualification workflow required; reference identities alone do not authenticate measurements',
        numerical_model_admitted=False,physical_design_changed=False,historical_results_mutated=False,
        complete_installed_mass_kg=None,complete_installed_cost_USD=None,selection_id=None,**FLAGS)
    result['evaluation_id']=identity(result);return result


def _relaxes(old,new):
    if old.get('operator')!=new.get('operator') or old.get('unit')!=new.get('unit'):return True
    a=old.get('limit');b=new.get('limit')
    if a is None:return b is None
    if b is None:return True
    return b>a if old['operator']=='max' else b<a if old['operator']=='min' else False


def review_proposal(current,proposed,*,candidate_id=None,rationale=None):
    """Review criterion changes; approval and physical generation are separate.

    current/proposed are criterion mappings, e.g. catalogue()['criteria']. A
    changed speed/target never creates a new physical identity by itself. New
    hardware must be generated and evaluated under its own physical definition.
    """
    old=_criteria(current);new=_criteria(proposed,proposal=True);changes=[];blocks=[];tasks=[]
    if candidate_id is not None and not _sha(candidate_id):raise ValueError('Explicit physical candidate SHA required')
    for uid in sorted(set(old)|set(new)):
        a=old.get(uid);b=new.get(uid)
        if a==b:continue
        category=a['category'] if a else b['category'];changes.append(dict(criterion_id=uid,category=category,before=a,after=b))
        if not rationale:blocks.append(dict(criterion_id=uid,reason='A documented engineering rationale is required'))
        if a and a['category']=='mandatory_obligation':
            if b is None or b['category']!='mandatory_obligation':blocks.append(dict(criterion_id=uid,reason='A mandatory obligation cannot be removed or demoted'))
            elif _relaxes(a,b) and (not _basis_supported(b,candidate_id) or b.get('provenance')==a.get('provenance')):blocks.append(dict(criterion_id=uid,reason='Hard-limit relaxation requires a new supported scope/provenance, never a target change'))
            elif a.get('limit')!=b.get('limit') and not _basis_supported(b,candidate_id):blocks.append(dict(criterion_id=uid,reason='A new quantitative hard limit requires derived scope and supported provenance'))
            tasks.append(dict(criterion_id=uid,kind='qualification-review',question='Derive interface/function limits and authenticate evidence, loads, uncertainty and independent review'))
        elif a and a['category']=='numerical_validity_domain':
            if b is None or b['category']!='numerical_validity_domain' or b.get('model_id')==a.get('model_id') and _relaxes(a,b):blocks.append(dict(criterion_id=uid,reason='Numerical model domain cannot be removed, demoted or extended by limit relaxation'))
            tasks.append(dict(criterion_id=uid,kind='new-model-validation',question='Bind the new model, material law, validity envelope and independent benchmarks; retain old results unchanged'))
        elif b and b['category']=='mandatory_obligation':
            if b.get('limit') is not None and not _basis_supported(b,candidate_id):blocks.append(dict(criterion_id=uid,reason='A new hard limit requires derived scope and supported provenance'))
            tasks.append(dict(criterion_id=uid,kind='qualification-review',question='Derive and support this obligation before using it as a hard screen'))
        else:
            tasks.append(dict(criterion_id=uid,kind='re-evaluate-system',question='Recompute affected interfaces, complete equipment and service consequences; target compliance alone does not establish suitability'))
    result=dict(schema='osr-requirement-revision-review/1',candidate_id=candidate_id,physical_candidate_id_unchanged=True,
        previous_requirement_revision=identity(old),proposed_requirement_revision=identity(new),changes=changes,blocks=blocks,next_tasks=tasks,
        disposition='blocked-unsupported-revision' if blocks else 'requires-new-evaluation-and-review' if changes else 'unchanged',
        integrated_suitability='unknown',automatic_acceptance=False,physical_generation_performed=False,
        historical_results_mutated=False,selection_id=None,source_sha256=catalogue()['source_sha256'],**FLAGS)
    result['review_id']=identity(result);return result
