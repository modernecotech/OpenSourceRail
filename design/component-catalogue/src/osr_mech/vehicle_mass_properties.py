"""Evidence-bound component scope, uncertainty, CG and individual axle loads.

These calculations do not close a product ledger or change a simulator startup.
Every physical item must be covered once; parent and child scopes may not overlap.
"""
from .industrialisation import nonnegative
from .provenance import stable_sum


def mass_properties(records,required_items,bodies,bogies):
    required=set(required_items);covered=set();seen=set();missing=[];rows=[]
    body_ids={b['id'] for b in bodies};bogie_ids={b['id'] for b in bogies}
    if len(body_ids)!=len(bodies) or len(bogie_ids)!=len(bogies):raise ValueError('distinct mass attachment identities required')
    for row in records:
        if row['id'] in seen:raise ValueError('duplicate mass record identity')
        seen.add(row['id']);scope=set(row['included_items'])
        if not scope or len(scope)!=len(row['included_items']) or not scope<=required or scope&covered:
            raise ValueError('mass scope is unknown, repeated or overlaps a parent/child record')
        covered|=scope
        if not row.get('evidence_record') or any(row.get(k) is None for k in ('mass_kg','uncertainty_kg','x_m','y_m','z_m')):
            missing.append(row['id']);continue
        mass=nonnegative(row['mass_kg'],'component mass');uncertainty=nonnegative(row['uncertainty_kg'],'mass uncertainty')
        if uncertainty>mass:raise ValueError('uncertainty cannot imply negative mass')
        if (row.get('body') in body_ids)+(row.get('bogie') in bogie_ids)!=1:
            raise ValueError('one identified body or direct bogie attachment required')
        import math
        if any(isinstance(row[k],bool) or not isinstance(row[k],(int,float)) or not math.isfinite(row[k]) for k in ('x_m','y_m','z_m')):raise ValueError('finite component mass location required')
        rows.append(row)
    absent=sorted(required-covered)
    if missing or absent:return dict(total_mass_kg=None,cg_m=None,axle_pattern=None,uncovered_items=absent,
        incomplete_records=missing,accepted_mass_closure=False,simulator_startup_replaced=False)
    total=stable_sum(r['mass_kg'] for r in rows)
    if total<=0:raise ValueError('positive total mass required')
    cg={axis:stable_sum(r['mass_kg']*r[axis+'_m'] for r in rows)/total for axis in ('x','y','z')}
    lower=stable_sum(r['mass_kg']-r['uncertainty_kg'] for r in rows);upper=stable_sum(r['mass_kg']+r['uncertainty_kg'] for r in rows)
    position_unknown=[r['id'] for r in rows if r.get('position_uncertainty_m') is None]
    cg_interval=None
    if not position_unknown and lower>0:
        cg_interval={}
        for axis in ('x','y','z'):
            lows=[];highs=[]
            for r in rows:
                delta=nonnegative(r['position_uncertainty_m'],'position uncertainty')
                corners=[m*x for m in (r['mass_kg']-r['uncertainty_kg'],r['mass_kg']+r['uncertainty_kg'])
                    for x in (r[axis+'_m']-delta,r[axis+'_m']+delta)]
                lows.append(min(corners));highs.append(max(corners))
            quotients=[n/d for n in (stable_sum(lows),stable_sum(highs)) for d in (lower,upper)]
            cg_interval[axis]=[min(quotients),max(quotients)]
    reactions={b['id']:0. for b in bogies}
    for body in bodies:
        supports=body['supports']
        if len(supports)!=2 or len(set(supports))!=2 or not set(supports)<=bogie_ids:raise ValueError('body needs two known supports')
        a,b=sorted(supports,key=lambda key:next(g['pivot_x_m'] for g in bogies if g['id']==key))
        left=next(g['pivot_x_m'] for g in bogies if g['id']==a);right=next(g['pivot_x_m'] for g in bogies if g['id']==b)
        if right<=left:raise ValueError('positive body support spacing required')
        body_rows=[r for r in rows if r.get('body')==body['id']]
        body_mass=stable_sum(r['mass_kg'] for r in body_rows)
        body_cg=stable_sum(r['mass_kg']*r['x_m'] for r in body_rows)/body_mass if body_mass else (left+right)/2
        if not left<=body_cg<=right:raise ValueError('body CG requires an explicit uplift/restraint load-path model')
        for r in rows:
            if r.get('body')!=body['id']:continue
            weight=r['mass_kg']*9.81/1000
            reactions[a]+=weight*(right-r['x_m'])/(right-left)
            reactions[b]+=weight*(r['x_m']-left)/(right-left)
    axles=[]
    for bogie in bogies:
        positions=sorted(bogie['axle_x_m'])
        if len(positions)!=2 or positions[0]>=positions[1] or not positions[0]<=bogie['pivot_x_m']<=positions[1]:
            raise ValueError('two distinct axles bracketing each bogie pivot required')
        direct=[r for r in rows if r.get('bogie')==bogie['id']]
        weight=reactions[bogie['id']]+stable_sum(r['mass_kg']*9.81/1000 for r in direct)
        moment=reactions[bogie['id']]*bogie['pivot_x_m']+stable_sum(r['mass_kg']*9.81/1000*r['x_m'] for r in direct)
        right=(moment-weight*positions[0])/(positions[1]-positions[0]);left=weight-right
        if min(left,right)<-1e-8:raise ValueError('mass arrangement produces unsupported axle uplift')
        axles.extend(dict(bogie=bogie['id'],axle=i+1,x_m=x,static_load_kn=w) for i,(x,w) in enumerate(zip(positions,(left,right))))
    return dict(total_mass_kg=total,total_mass_interval_kg=[lower,upper],cg_m=cg,cg_interval_m=cg_interval,
        missing_position_uncertainty_records=position_unknown,axle_pattern=axles,
        uncertainty_is_worst_case_mass_sum=True,load_balance_passed=abs(stable_sum(a['static_load_kn'] for a in axles)-total*9.81/1000)<1e-7,
        accepted_mass_closure=False,simulator_startup_replaced=False,engineering_accepted=False,
        limitations='Static vertical two-support bodies and two-axle bogies; lateral, fatigue, crash and dynamic load paths require design.')
