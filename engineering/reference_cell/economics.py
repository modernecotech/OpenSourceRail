"""Same-service conditional lifecycle costs with explicit missing charge scopes.

Cashflow coverage is a declared calendar of physical item/operation charges. A
known subtotal is never a complete railway price. Grade/part occurrences and the
cost classes retain their source/candidate bindings; this module issues no orders
and never chooses a physically unqualified integrated winner.
"""
from copy import deepcopy
from math import fsum,isfinite
from datetime import date
from . import identity,FLAGS,digest
from . import manufacturing
from pathlib import Path

PRODUCER="engineering/reference_cell/economics.py"

def sources():
    return {PRODUCER:digest(__file__),"engineering/reference_cell/manufacturing.py":digest(manufacturing.__file__)}
from .manufacturing import SCOPES


def _hash(v):return isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)

def _text(v,name):
    if not isinstance(v,str) or not v.strip():raise ValueError('Nonempty '+name+' required')
    return v


def _interval(v,name):
    if not isinstance(v,(list,tuple)) or len(v)!=2 or any(type(x) not in (int,float) or not isfinite(x) or x<0 for x in v) or v[0]>v[1]:
        raise ValueError('Finite ordered nonnegative '+name+' interval required')
    return [float(x) for x in v]


def _paths(v,name):
    if not isinstance(v,list) or not v or any(not isinstance(x,str) or not x.strip() or x.startswith('/') or ':' in x or '..' in x.split('/') for x in v) or len(v)!=len(set(v)):
        raise ValueError('Distinct canonical relative '+name+' identifiers required')
    return v


def _service(s):
    if not isinstance(s,dict):raise ValueError('Explicit service context required')
    required=('cars','car_length_m','normal_places_per_car','headway_s','station_spacing_m','fleet_trainsets')
    for key in required:
        v=s.get(key)
        if type(v) not in (int,float) or not isfinite(v) or v<=0:raise ValueError('Positive service '+key+' required')
    for key in ('cars','normal_places_per_car','fleet_trainsets'):
        if type(s[key]) is not int:raise ValueError('Integer service '+key+' required')
    # These retain transport output and risk/approval context, rather than letting
    # an unprotected 2-minute arithmetic headway count as qualified capacity.
    context={k:deepcopy(v) for k,v in s.items() if k not in ('required_cashflows','required_scope_items','candidate_id','service_context_id')}
    normal=s['cars']*s['normal_places_per_car']*3600/s['headway_s']
    if s.get('normal_capacity_pphpd') is not None and abs(s['normal_capacity_pphpd']-normal)>1e-7*max(1.,normal):raise ValueError('Capacity must match formation/headway arithmetic')
    return context,identity(context),normal


def make_record(candidate_id,scope,physical_scope,quantity,unit_cost_usd,year,source_class,source_id,
                source_date,location,quantity_basis,service_context_id,**extra):
    value=dict(schema='osr-lifecycle-charge-record/1',candidate_id=candidate_id,scope=scope,
        physical_scope=list(physical_scope),quantity=list(quantity),unit_cost_usd=list(unit_cost_usd),year=year,
        source_class=source_class,source_id=source_id,source_date=source_date,location=location,
        quantity_basis=quantity_basis,currency='USD',service_context_id=service_context_id,**deepcopy(extra))
    value['record_id']=identity(value);return value


def service_identity(service_context):return _service(service_context)[1]


def _calendar(service,years):
    rows=service.get('required_cashflows')
    if rows is None:return None
    if not isinstance(rows,list) or not rows:raise ValueError('Nonempty explicit required cashflow calendar or absent input required')
    expected={scope:set() for scope in SCOPES}
    all_keys=set()
    for row in rows:
        if not isinstance(row,dict) or row.get('scope') not in SCOPES:raise ValueError('Calendar scope invalid')
        y=row.get('year')
        if type(y) is not int or not 0<=y<=years:raise ValueError('Calendar charge year outside design horizon')
        _paths([row.get('physical_scope')],'calendar charge')
        key=(y,row['physical_scope'])
        if key in all_keys:raise ValueError('Required charge calendar duplicates item/year across scopes')
        all_keys.add(key);expected[row['scope']].add(key)
    if any(not keys for keys in expected.values()):raise ValueError('Required charge calendar must explicitly cover all twelve whole-life scopes')
    return expected


def evaluate(candidate_id,records,years,discount_rate,service_context,*,authenticator=None,authentication_context_id=None):
    if not _hash(candidate_id):raise ValueError('Exact physical candidate identity required')
    if type(years) is not int or not 1<=years<=100:raise ValueError('Integer lifecycle horizon 1–100 years required')
    if type(discount_rate) not in (int,float) or not isfinite(discount_rate) or not 0<=discount_rate<=1:
        raise ValueError('Explicit finite discount fraction 0–1 required')
    if not isinstance(records,(list,tuple)) or len(records)>100000:raise ValueError('Bounded explicit lifecycle records required')
    if authenticator is not None and (not callable(authenticator) or not _hash(authentication_context_id)):
        raise ValueError('Trusted external authentication callback and context identity required')
    context,service_id,capacity=_service(service_context);calendar=_calendar(service_context,years)
    claimed={};record_ids=set();assessed=[];coverage={s:set() for s in SCOPES};cash={s:[] for s in SCOPES};held=[]
    for record in records:
        r=deepcopy(record)
        if r.get('schema')!='osr-lifecycle-charge-record/1' or r.get('record_id')!=identity({k:v for k,v in r.items() if k!='record_id'}):raise ValueError('Lifecycle charge record identity/schema differs')
        if r.get('record_id') in record_ids:raise ValueError('Duplicate lifecycle charge record')
        record_ids.add(r['record_id'])
        if r.get('candidate_id')!=candidate_id or r.get('service_context_id')!=service_id:raise ValueError('Mixed physical candidate or service basis')
        if any(r.get(flag) is not False for flag in FLAGS if flag in r):raise ValueError('Cost records cannot issue physical acceptance or release')
        scope=r.get('scope');y=r.get('year')
        if scope not in SCOPES or type(y) is not int or not 0<=y<=years:raise ValueError('Supported whole-life scope/year required')
        paths=_paths(r.get('physical_scope'),'item/operation charge')
        for path in paths:
            for (existing_year,existing),owner in claimed.items():
                if y==existing_year and (path==existing or path.startswith(existing+'/') or existing.startswith(path+'/')):
                    raise ValueError('Overlapping/double-counted physical item/operation cost scope')
            claimed[y,path]=r['record_id']
            if calendar is not None and (y,path) not in calendar[scope]:raise ValueError('Charge outside its declared complete lifecycle calendar')
        quantity=_interval(r.get('quantity'),'quantity');unit=_interval(r.get('unit_cost_usd'),'unit cost')
        if quantity[0]<=0:raise ValueError('Explicit positive charge quantity required')
        if r.get('source_class') not in ('A','B','C') or r.get('currency')!='USD':raise ValueError('Traceable A/B/C USD record required; retain actual conversion source upstream')
        if not _hash(r.get('source_id')):raise ValueError('Immutable cost source identity required')
        for key in ('source_date','location','quantity_basis'):_text(r.get(key),key)
        when=date.fromisoformat(r['source_date'])
        if context.get('estimate_date') is not None and when>date.fromisoformat(context['estimate_date']):raise ValueError('Cost source postdates estimate date')
        if r.get('source_class')=='A':
            if not _hash(r.get('source_document_sha256')) or not r.get('supplier') or not r.get('valid_until'):raise ValueError('Class A source document, supplier and validity required')
            until=date.fromisoformat(r['valid_until'])
            if until<when or context.get('estimate_date') is not None and until<date.fromisoformat(context['estimate_date']):raise ValueError('Actual quote/cost source is not valid for estimate')
            authenticated=authenticator is not None and authenticator(r,'lifecycle-source') is True
        else:
            _text(r.get('method'),'estimate derivation method')
            authenticated=False
        admitted=r['source_class']!='A' or authenticated
        total=[quantity[i]*unit[i] for i in range(2)]
        discounted=[v/(1+discount_rate)**y for v in total]
        row=dict(record_id=r['record_id'],scope=scope,physical_scope=paths,year=y,source_class=r['source_class'],source_id=r['source_id'],
            quantity=quantity,unit_cost_usd=unit,total_usd=total,npv_usd=discounted,
            currency='USD',source_date=r['source_date'],location=r['location'],quantity_basis=r['quantity_basis'],
            supplier=r.get('supplier'),valid_until=r.get('valid_until'),source_document_sha256=r.get('source_document_sha256'),
            externally_authenticated=authenticated,admitted_to_conditional_subtotal=admitted,
            confidence='authenticated actual source; engineering/installed scope remains separately open' if authenticated else 'engineering estimate' if r['source_class']=='B' else 'explicit placeholder range' if r['source_class']=='C' else 'held missing external authentication')
        assessed.append(row)
        if admitted:
            coverage[scope].update((y,p) for p in paths);cash[scope].append(row)
        else:held.append(r['record_id'])
    scopes={};missing=[]
    for scope in SCOPES:
        rows=cash[scope];expected=None if calendar is None else calendar[scope]
        absent=None if expected is None else sorted(expected-coverage[scope])
        complete=expected is not None and not absent
        if not complete:missing.append(scope)
        scopes[scope]=dict(known_charge_count=len(rows),known_scope_npvs_usd=[fsum(r['npv_usd'][i] for r in rows) for i in range(2)],
            conditional_complete_scope_npv_usd=None if not complete else [fsum(r['npv_usd'][i] for r in rows) for i in range(2)],
            required_charge_count=None if expected is None else len(expected),covered_charge_count=len(coverage[scope]),
            missing_charge_ids=absent,complete_for_declared_calendar=complete)
    accepted=[r for r in assessed if r['admitted_to_conditional_subtotal']]
    annual=[dict(year=y,known_scope_usd=[fsum(r['total_usd'][i] for r in accepted if r['year']==y) for i in range(2)],
        known_scope_npv_usd=[fsum(r['npv_usd'][i] for r in accepted if r['year']==y) for i in range(2)]) for y in range(years+1)]
    subtotal=[fsum(r['npv_usd'][i] for r in accepted) for i in range(2)]
    # This ranks only supported interval widths, not probabilities, expected
    # utility or an invented value of information for an unpriced component.
    sensitivity=sorted([dict(record_id=r['record_id'],scope=r['scope'],npv_bound_width_usd=r['npv_usd'][1]-r['npv_usd'][0],
        action='seek source/measurement to reduce this declared range',source_class=r['source_class']) for r in accepted if r['source_class']!='A'],key=lambda x:(-x['npv_bound_width_usd'],x['record_id']))
    required_count=None if calendar is None else sum(len(v) for v in calendar.values())
    actual_count=sum(len(r['physical_scope']) for r in accepted if r['source_class']=='A')
    estimated_count=sum(len(r['physical_scope']) for r in accepted if r['source_class'] in ('B','C'))
    result=dict(schema='osr-conditional-lifecycle-economics/1',source_sha256=sources(),candidate_id=candidate_id,service_context=context,service_context_id=service_id,
        years=years,discount_rate=discount_rate,normal_capacity_pphpd=capacity,
        source_record_ids=sorted(record_ids),authentication_context_id=authentication_context_id,
        records=assessed,scopes=scopes,annual=annual,known_scope_npv_usd=subtotal,
        conditional_declared_calendar_npv_usd=subtotal if not missing else None,
        complete_installed_whole_life_cost_usd=None,declared_calendar_complete=not missing,
        missing_whole_life_scopes=missing,unbounded_missing_quotes_or_measurements=missing,
        actual_authenticated_charge_count=actual_count,estimated_charge_count=estimated_count,
        required_charge_count=required_count,
        actual_quote_coverage=None if required_count is None else actual_count/required_count,
        conditional_estimate_coverage=None if required_count is None else (actual_count+estimated_count)/required_count,
        held_actual_source_record_ids=held,sensitivity_bound_width_ranking=sensitivity,
        bound_ranking_is_value_of_information=False,integrated_winner=None,
        open_protection_or_evidence=not (context.get('protected_service_qualified') is True and context.get('engineering_evidence_qualified') is True),**FLAGS)
    result['evaluation_id']=identity(result);return result


def compare(results):
    if not isinstance(results,list) or not results:raise ValueError('Nonempty lifecycle results required')
    first=results[0];ids=set()
    for r in results:
        if r.get('schema')!='osr-conditional-lifecycle-economics/1' or r.get('evaluation_id')!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Lifecycle evaluation identity differs')
        if r.get('source_sha256')!=sources():raise ValueError('Lifecycle calculation source epoch differs')
        if r['candidate_id'] in ids:raise ValueError('Select one economics evaluation per physical candidate explicitly')
        ids.add(r['candidate_id'])
        if (r['service_context_id'],r['years'],r['discount_rate'])!=(first['service_context_id'],first['years'],first['discount_rate']):raise ValueError('Equal formation/capacity/headway/fleet/route/risk/protection basis required')
    complete=[r for r in results if r['conditional_declared_calendar_npv_usd'] is not None]
    # Disjoint intervals demonstrate robust conditional cost ordering only.
    ordering=[]
    for r in complete:
        dominated_by=[p['candidate_id'] for p in complete if p['candidate_id']!=r['candidate_id'] and p['conditional_declared_calendar_npv_usd'][1]<r['conditional_declared_calendar_npv_usd'][0]]
        ordering.append(dict(candidate_id=r['candidate_id'],robustly_more_expensive_than=dominated_by))
    value=dict(schema='osr-equal-service-cost-comparison/1',source_sha256=sources(),service_context_id=first['service_context_id'],
        evaluation_ids=[r['evaluation_id'] for r in results],candidate_ids=[r['candidate_id'] for r in results],
        conditional_interval_ordering=ordering,unknown_cost_candidates=[r['candidate_id'] for r in results if r['conditional_declared_calendar_npv_usd'] is None],
        integrated_winner=None,selection_purpose='conditional-cost-evidence-review-only',**FLAGS)
    value['evaluation_id']=identity(value);return value
