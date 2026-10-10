"""Evidence-bound component scope, uncertainty, CG and individual axle loads.

These calculations do not close a product ledger or change a simulator startup.
Every physical item must be covered once; parent and child scopes may not overlap.
"""
from .industrialisation import nonnegative
from .provenance import stable_sum


def inertia_tensor(value, label='component inertia'):
    """Validate a physical tensor about its own CG, in kg m²."""
    import numpy as np
    a = np.asarray(value)
    if a.shape != (3, 3) or a.dtype.kind not in 'if' or not np.isfinite(a).all():
        raise ValueError(label + ' must be a finite 3x3 tensor')
    a = a.astype(float)
    if not np.allclose(a, a.T, atol=1e-10, rtol=1e-10):
        raise ValueError(label + ' must be symmetric')
    principal = np.linalg.eigvalsh(a)
    if principal[0] < -1e-10 or principal[-1] > principal[:2].sum() + 1e-8:
        raise ValueError(label + ' must satisfy physical principal inertia inequalities')
    return a


def combined_inertia(rows, cg, cg_interval):
    """Rotate local tensors and apply the parallel-axis theorem once per scope.

    Component uncertainty is an absolute spectral bound. Interval arithmetic
    gives a conservative enclosure, retaining correlation losses explicitly.
    """
    import numpy as np
    unknown = [r['id'] for r in rows if r.get('inertia_tensor_kg_m2') is None]
    if unknown:
        return dict(inertia_tensor_kg_m2=None, inertia_interval_kg_m2=None,
                    missing_inertia_records=unknown)
    result = np.zeros((3, 3)); intervals = np.zeros((3, 3, 2))
    bounded = cg_interval is not None
    def multiply(a, b):
        v = [x*y for x in a for y in b]
        return min(v), max(v)
    def square(a):
        return (0. if a[0] <= 0 <= a[1] else min(x*x for x in a), max(x*x for x in a))
    for row in rows:
        local = inertia_tensor(row['inertia_tensor_kg_m2'])
        rotation = np.asarray(row.get('rotation_matrix', np.eye(3)))
        if (rotation.shape != (3, 3) or rotation.dtype.kind not in 'if' or
            not np.isfinite(rotation).all() or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-10) or
            not np.isclose(np.linalg.det(rotation), 1., atol=1e-10)):
            raise ValueError('mass transform needs a proper orthonormal rotation')
        local = rotation @ local @ rotation.T
        delta = np.asarray([row[k+'_m']-cg[k] for k in ('x', 'y', 'z')])
        result += local + row['mass_kg']*(np.eye(3)*np.dot(delta, delta)-np.outer(delta, delta))
        uncertainty = row.get('inertia_uncertainty_kg_m2')
        if uncertainty is None or row.get('position_uncertainty_m') is None or cg_interval is None:
            bounded = False
            continue
        uncertainty = nonnegative(uncertainty, 'inertia uncertainty')
        dr = row['position_uncertainty_m']
        offsets = [(row[k+'_m']-dr-cg_interval[k][1], row[k+'_m']+dr-cg_interval[k][0]) for k in ('x', 'y', 'z')]
        mass = (row['mass_kg']-row['uncertainty_kg'], row['mass_kg']+row['uncertainty_kg'])
        for i in range(3):
            for j in range(3):
                if i == j:
                    terms = [square(offsets[k]) for k in range(3) if k != i]
                    shift = multiply(mass, (sum(v[0] for v in terms), sum(v[1] for v in terms)))
                else:
                    value = multiply(mass, multiply(offsets[i], offsets[j]))
                    shift = (-value[1], -value[0])
                intervals[i, j] += [local[i, j]-uncertainty+shift[0], local[i, j]+uncertainty+shift[1]]
    return dict(inertia_tensor_kg_m2=result.tolist(), inertia_interval_kg_m2=intervals.tolist() if bounded else None,
                missing_inertia_records=[], inertia_reference='total centre of gravity, global XYZ',
                inertia_uncertainty_basis='conservative intervals; correlated CG/mass bounds enclosed independently')


def _wheel_reactions(rows, bodies, bogies):
    """Four-wheel rectangular support interpolation, preserving all static moments."""
    import itertools
    bogie_by_id = {b['id']: b for b in bogies}
    reactions = {}
    intervals = {}
    for bogie in bogies:
        xs = sorted(bogie['axle_x_m']); ys = bogie.get('rail_y_m', [-.7175, .7175])
        if len(ys) != 2 or ys[0] >= ys[1]:
            raise ValueError('two ordered rail lateral positions required')
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                key = (bogie['id'], i+1, j)
                reactions[key] = 0.; intervals[key] = [0., 0.]
    bounded = all(r.get('position_uncertainty_m') is not None for r in rows)
    for row in rows:
        if row.get('body'):
            body = next(b for b in bodies if b['id'] == row['body'])
            supports = sorted(body['supports'], key=lambda s: bogie_by_id[s]['pivot_x_m'])
        else:
            supports = [row['bogie']]
        for support in supports:
            bogie = bogie_by_id[support]
            xs = sorted(bogie['axle_x_m']); ys = bogie.get('rail_y_m', [-.7175, .7175])
            def load(m, x, y, i, j):
                if row.get('body'):
                    left, right = (bogie_by_id[s]['pivot_x_m'] for s in supports)
                    longitudinal = (right-x)/(right-left) if support == supports[0] else (x-left)/(right-left)
                    axle_x = bogie['pivot_x_m']
                else:
                    longitudinal, axle_x = 1., x
                longitudinal *= (xs[1]-axle_x)/(xs[1]-xs[0]) if i == 0 else (axle_x-xs[0])/(xs[1]-xs[0])
                lateral = (ys[1]-y)/(ys[1]-ys[0]) if j == 0 else (y-ys[0])/(ys[1]-ys[0])
                return m*9.81/1000*longitudinal*lateral
            for i in range(2):
                for j in range(2):
                    key = (support, i+1, j)
                    reactions[key] += load(row['mass_kg'], row['x_m'], row['y_m'], i, j)
                    if bounded:
                        dp = row['position_uncertainty_m']; dm = row['uncertainty_kg']
                        values = [load(m, x, y, i, j) for m, x, y in itertools.product(
                            [row['mass_kg']-dm, row['mass_kg']+dm], [row['x_m']-dp, row['x_m']+dp], [row['y_m']-dp, row['y_m']+dp])]
                        intervals[key][0] += min(values); intervals[key][1] += max(values)
    wheels = []
    for (support, axle, rail), weight in reactions.items():
        bogie = bogie_by_id[support]
        if weight < -1e-8:
            raise ValueError('asymmetric mass arrangement requires a wheel uplift/restraint model')
        wheels.append(dict(bogie=support, axle=axle, rail=rail, x_m=sorted(bogie['axle_x_m'])[axle-1],
                           y_m=bogie.get('rail_y_m', [-.7175, .7175])[rail], static_load_kn=weight,
                           static_load_interval_kn=intervals[(support, axle, rail)] if bounded else None))
    return wheels


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
    wheels = _wheel_reactions(rows, bodies, bogies)
    wheel_by_axle = {}
    for wheel in wheels:
        wheel_by_axle.setdefault((wheel['bogie'], wheel['axle']), []).append(wheel)
    for axle in axles:
        members = wheel_by_axle[(axle['bogie'], axle['axle'])]
        axle['static_load_interval_kn'] = [sum(w['static_load_interval_kn'][i] for w in members) for i in range(2)] if all(w['static_load_interval_kn'] is not None for w in members) else None
    inertia = combined_inertia(rows, cg, cg_interval)
    return dict(total_mass_kg=total,total_mass_interval_kg=[lower,upper],cg_m=cg,cg_interval_m=cg_interval,
        **inertia, wheel_pattern=wheels,
        missing_position_uncertainty_records=position_unknown,axle_pattern=axles,
        uncertainty_is_worst_case_mass_sum=True,load_balance_passed=abs(stable_sum(a['static_load_kn'] for a in axles)-total*9.81/1000)<1e-7,
        accepted_mass_closure=False,simulator_startup_replaced=False,engineering_accepted=False,
        limitations='Static two-support bodies and rectangular four-wheel bogies; lateral wheel split assumes separable rectangular support interpolation. Track cant, roll stiffness, fatigue, crash and dynamic load paths require design.')
