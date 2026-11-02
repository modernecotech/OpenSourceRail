"""Robust Pareto comparisons of explicitly scoped partial research quantities.

Missing values are incomparable, never zero. Interval dominance must hold for
every value in both declared intervals. A partial-stock frontier cannot select
an economic, engineering-qualified or operational winner.
"""
from math import isfinite
import re
from engineering.station_rail.common import identity

FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)


def _sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
def _finite(value):return type(value) in (float,int) and isfinite(value)


def _interval(row,name):
    q=row.get('quantities',{}).get(name)
    if q is None:return None,'quantity-unavailable:'+name
    if not isinstance(q,dict) or not isinstance(q.get('unit'),str) or not q['unit'] or not isinstance(q.get('scope'),str) or not q['scope']:raise ValueError('Typed objective unit and quantity scope required')
    if q.get('value') is None and q.get('interval') is None:return None,'quantity-unknown:'+name
    interval=q.get('interval')
    if interval is None:
        if not _finite(q.get('value')):raise ValueError('Finite objective value or explicit unknown required')
        interval=[q['value'],q['value']]
    if not isinstance(interval,(list,tuple)) or len(interval)!=2 or not all(_finite(x) for x in interval) or interval[0]>interval[1]:raise ValueError('Finite ordered uncertainty interval required')
    if q.get('value') is not None and (not _finite(q['value']) or not interval[0]<=q['value']<=interval[1]):raise ValueError('Objective point must lie inside its declared uncertainty interval')
    return dict(lower=interval[0],upper=interval[1],unit=q['unit'],scope=q['scope']),None


def pareto(rows,objectives=None):
    """Keep incomparable/unknown candidates under matching comparison scopes.

    Each row has candidate_id, comparison_scope_id and quantities[name] with
    value (or None), unit, scope and optional [lower,upper] interval. Objectives
    map quantity names to min/max. Inputs can be inventory records or explicit
    source-bound aggregate rows prepared by the coordinator.
    """
    objectives={'known_gross_structure_stock_kg':'min','manufacturing_occurrences':'min','assembly_interfaces':'min'} if objectives is None else dict(objectives)
    if not objectives or any(not isinstance(n,str) or d not in ('min','max') for n,d in objectives.items()):raise ValueError('Explicit nonempty min/max objective policy required')
    rows=list(rows);ids=[]
    for r in rows:
        if not isinstance(r,dict) or not _sha(r.get('candidate_id')) or not _sha(r.get('comparison_scope_id')) or not isinstance(r.get('quantities'),dict):raise ValueError('Candidate, common-comparison scope and typed quantities required')
        if 'evaluation_id' in r and r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Source evaluation identity differs')
        ids.append(r['candidate_id'])
    if len(set(ids))!=len(ids):raise ValueError('One aggregate evaluation per candidate required; do not mix scenario rows')
    values={};unknown=[]
    for row in rows:
        values[row['candidate_id']]={}
        for name in objectives:
            value,reason=_interval(row,name);values[row['candidate_id']][name]=value
            if reason:unknown.append(dict(candidate_id=row['candidate_id'],reason=reason))
    edges=[];incomparable=[]
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            reason=None
            if a['comparison_scope_id']!=b['comparison_scope_id']:reason='different-service-or-account-comparison-scope'
            pairs=[]
            for name,direction in objectives.items():
                av=values[a['candidate_id']][name];bv=values[b['candidate_id']][name]
                if av is None or bv is None:reason=reason or 'unknown-objective; no dominance can be established'
                elif av['unit']!=bv['unit'] or av['scope']!=bv['scope']:reason=reason or 'different-objective-unit-or-quantity-scope'
                else:pairs.append((av,bv,direction))
            if reason:
                incomparable.append(dict(a=a['candidate_id'],b=b['candidate_id'],reason=reason));continue
            def dominates(reverse=False):
                comparisons=[];strict=[]
                for av,bv,direction in pairs:
                    if reverse:av,bv=bv,av
                    comparisons.append(av['upper']<=bv['lower'] if direction=='min' else av['lower']>=bv['upper'])
                    strict.append(av['upper']<bv['lower'] if direction=='min' else av['lower']>bv['upper'])
                return all(comparisons) and any(strict)
            if dominates():edges.append(dict(dominator=a['candidate_id'],dominated=b['candidate_id']))
            elif dominates(True):edges.append(dict(dominator=b['candidate_id'],dominated=a['candidate_id']))
            else:incomparable.append(dict(a=a['candidate_id'],b=b['candidate_id'],reason='trade-off-equality-or-overlapping-uncertainty'))
    dominated={e['dominated'] for e in edges}
    result=dict(schema='osr-scoped-partial-Pareto/1',objectives=objectives,input_evaluation_ids=[r.get('evaluation_id') for r in rows],
        nondominated_candidate_ids=[n for n in ids if n not in dominated],dominance_edges=edges,incomparable_pairs=incomparable,
        unknown_objectives=unknown,selection_purpose='retain-partial-quantity-alternatives',
        economic_winner=None,qualified_winner=None,scope='No complete installed cost/feasibility ranking is inferred from partial known quantities',**FLAGS)
    result['comparison_id']=identity(result);return result
