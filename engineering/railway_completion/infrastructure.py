"""Candidate-bound dead-stock and moving-axle loads on the actual span grid.

Wayside primaries are not weightless. Known solids enter the same guideway
support vector as the concrete/rail stock. Unlocated accounts retain placement
uncertainty; a uniform named-span distribution is an explicit hypothesis only.
No foundation, pier, station equipment or structural acceptance is inferred.
"""
from math import asin, fsum, pi, sqrt
from pathlib import Path
import re

import numpy as np

from engineering.station_rail import civil
from engineering.station_rail.common import identity,digest
from engineering.railway_twin import geometry
from engineering.design_search import railway_bundle
from . import FLAGS

PRODUCER='engineering/railway_completion/infrastructure.py'


def _uniform(a,b,force,source,scope):
    if b<=a:raise ValueError('Positive projected material extent required')
    return dict(kind='uniform',a_m=float(a),b_m=float(b),force_N=float(force),
        source_occurrence_id=source,projection_scope=scope)


def _disk_integrals(radius,z):
    z=min(radius,max(-radius,z));s=sqrt(max(0.,radius*radius-z*z))
    return z*s+radius*radius*asin(z/radius),-2*s**3/3


def _integral(segment,lo,hi,*,point_span=None):
    """Return load force and its first moment in a clipped longitudinal slice."""
    a,b=segment['a_m'],segment['b_m'];left=max(lo,a);right=min(hi,b)
    if segment['kind']=='point':
        x=segment['x_m']
        inside=(lo<=x<=hi and (point_span is None or point_span==segment['span_index']))
        return (segment['force_N'],segment['force_N']*x) if inside else (0.,0.)
    if right<=left:return 0.,0.
    if segment['kind']=='uniform':
        q=segment['force_N']/(b-a)
        return q*(right-left),q*(right*right-left*left)/2
    radius=segment['radius_m'];center=segment['center_m'];scale=segment['force_N']/(pi*radius*radius)
    A0,Q0=_disk_integrals(radius,left-center);A1,Q1=_disk_integrals(radius,right-center)
    force=scale*(A1-A0)
    return force,center*force+scale*(Q1-Q0)


def _projection(row,primitive):
    p=row['geometry'];shift=np.asarray(row['translation_m']);name=row['id'];mass=row['mass_kg'];rhoG=mass*civil.G/primitive['volume']
    rows=[];scope='exact-uniform-density-material-projection'
    if p['kind'] in ('box','box-with-rectangular-cutouts'):
        size=np.asarray(p['size_m']);at=np.asarray(p['at_m'])+shift
        rows.append(_uniform(at[0],at[0]+size[0],float(np.prod(size))*rhoG,name,scope))
        for cut in primitive['voids']:
            if cut['kind']=='box':
                start=cut['at'][0]+shift[0]
                rows.append(_uniform(start,start+cut['size'][0],-cut['volume']*rhoG,name,scope))
            elif abs(cut['axis'][0])>1-1e-10:
                a=cut['at'][0]+shift[0];b=a+cut['axis'][0]*cut['length']
                rows.append(_uniform(min(a,b),max(a,b),-cut['volume']*rhoG,name,scope))
            elif abs(cut['axis'][0])<1e-10:
                center=cut['cg'][0]+shift[0];radius=cut['radius']
                rows.append(dict(kind='disk',a_m=center-radius,b_m=center+radius,center_m=center,radius_m=radius,
                    force_N=-cut['volume']*rhoG,source_occurrence_id=name,projection_scope=scope))
            else:raise ValueError('Oblique bores require a projected material-slice evaluator')
    elif p['kind']=='oriented-RHS' and np.allclose(np.abs(primitive['basis']).sum(axis=0),1.,atol=1e-10,rtol=0):
        for sign,w,h in ((1,primitive['width'],primitive['height']),(-1,primitive['width']-2*primitive['wall'],primitive['height']-2*primitive['wall'])):
            R=primitive['basis'];L=primitive['length'];at=primitive['origin']
            points=np.array([at+R@np.array([x,y,z])+shift for x in (-w/2,w/2) for y in (-h/2,h/2) for z in (0.,L)])
            a,b=float(points[:,0].min()),float(points[:,0].max())
            rows.append(_uniform(a,b,sign*w*h*L*rhoG,name,scope))
    elif p['kind'] in ('cylinder','annular-cylinder') and abs(primitive['basis'][0,2])>1-1e-10:
        a=primitive['lo'][0]+shift[0];b=primitive['hi'][0]+shift[0]
        rows.append(_uniform(a,b,mass*civil.G,name,scope))
    elif p['kind'] in ('cylinder','annular-cylinder') and abs(primitive['basis'][0,2])<1e-10:
        center=primitive['cg'][0]+shift[0]
        for sign,radius in ((1,primitive['radius']),(-1,primitive['inner'])):
            if radius<=0:continue
            rows.append(dict(kind='disk',a_m=float(center-radius),b_m=float(center+radius),center_m=float(center),radius_m=radius,
                force_N=sign*pi*radius*radius*primitive['length']*rhoG,source_occurrence_id=name,projection_scope=scope))
    else:
        # The centroid-equivalent point preserves resultant and first moment,
        # but is not an actual material distribution or a certified load bound.
        x=float(primitive['cg'][0]+shift[0]);a=float(primitive['lo'][0]+shift[0]);b=float(primitive['hi'][0]+shift[0])
        rows.append(dict(kind='point',a_m=x,b_m=x,x_m=x,force_N=mass*civil.G,
            occupied_interval_m=[a,b],source_occurrence_id=name,
            projection_scope='centroid-lumped-hypothesis; oblique material projection unsupported'))
    return rows


def _point_owner(x,start,end,span):
    count=int(round((end-start)/span))
    if x<start or x>end:return -1
    return min(count-1,max(0,int((x-start)//span)))


def _span_response(a,b,segments,index):
    parts=[r for r in segments if r['b_m']>=a and r['a_m']<=b and (r['kind']!='point' or r['span_index']==index)]
    loads=[_integral(r,a,b,point_span=index) for r in parts]
    force=fsum(p for p,q in loads);moment=fsum(q for p,q in loads);L=b-a
    left=(b*force-moment)/L;right=(moment-a*force)/L
    def prefix(x):
        values=[]
        for row in parts:
            if row['kind']=='point' and row['x_m']>=x:continue
            values.append(_integral(row,a,x,point_span=index))
        return fsum(p for p,q in values),fsum(q for p,q in values)
    def bending(x):
        p,q=prefix(x)
        return left*(x-a)-x*p+q
    def shear(x):return left-prefix(x)[0]
    cuts=sorted({a,b,*[max(a,min(b,x)) for row in parts for x in (row['a_m'],row['b_m'])]})
    candidates=set(cuts)
    for lo,hi in zip(cuts,cuts[1:]):
        epsilon=min((hi-lo)/1000,1e-8)
        low,high=lo+epsilon,hi-epsilon
        if high<=low:continue
        vl,vh=shear(low),shear(high)
        if vl>=0 and vh<=0:
            for _ in range(50):
                middle=(low+high)/2
                if shear(middle)>0:low=middle
                else:high=middle
            candidates.add((low+high)/2)
    sample=sorted(candidates|{a+i*L/40 for i in range(41)})
    curve=[dict(x_m=x,dead_moment_Nm=bending(x),dead_shear_N=shear(x)) for x in sample]
    peak=max(curve,key=lambda r:r['dead_moment_Nm'])
    return dict(span_index=index,start_m=a,end_m=b,known_dead_force_N=force,known_dead_first_moment_Nm=moment,
        left_reaction_N=left,right_reaction_N=right,force_residual_N=left+right-force,
        moment_residual_Nm=left*a+right*b-moment,peak_dead_moment_Nm=peak['dead_moment_Nm'],
        peak_dead_moment_chainage_m=peak['x_m'],moment_curve=curve)


def derive(scene,bundle,ledger=None):
    """Project disjoint source stock and supplied named-span account hypotheses.

    With no ledger, unlocated accounting coverage is explicitly missing. The
    supported results remain partial loads, not complete installed beam demands.
    """
    candidate=bundle['candidate_id']
    test_only=bundle.get('schema')=='osr-infrastructure-method-test/1'
    if not test_only:railway_bundle.validate(bundle)
    if scene.get('candidate_id')!=candidate or ledger is not None and ledger.get('candidate_id')!=candidate:
        raise ValueError('Infrastructure loads cannot mix candidate/ledger identities')
    geometry.validate_scene(scene)
    if ledger is not None:
        if ledger.get('scene_id',identity(scene))!=identity(scene):raise ValueError('Infrastructure account ledger uses another scene')
        ids=[r['id'] for r in ledger['unlocated_accounts']]
        if len(ids)!=len(set(ids)) or set(ids)&{r['id'] for r in scene['occurrences']}:
            raise ValueError('Disjoint unique stock and unlocated account occurrences required')
    route=bundle['architecture_case']['physical_definition']['route']
    start=float(route['counted_guideway_start_m']);end=float(route['counted_guideway_end_m'])
    span=float(bundle['architecture_case']['physical_definition']['guideway']['span_m'])
    if span!=20. or end<=start or abs((end-start)/span-round((end-start)/span))>1e-9:
        raise ValueError('Explicit whole20m canonical span coverage required')
    dead=[r for r in scene['occurrences'] if not r['system'].startswith('vehicle/')]
    segments=[];projection_hypotheses=[]
    force=moment=wayside=0.
    for row in dead:
        primitive=geometry._primitive(row['geometry'])
        if not np.isfinite(row['mass_kg']) or row['mass_kg']<=0:raise ValueError('Positive finite known-stock mass required')
        if abs(row['geometry'].get('mass_kg',row['mass_kg'])-row['mass_kg'])>1e-7:raise ValueError('Scene stock mass differs')
        rows=_projection(row,primitive)
        for line in rows:
            if line['kind']=='point':
                line['span_index']=_point_owner(line['x_m'],start,end,span)
                projection_hypotheses.append(dict(occurrence_id=row['id'],occupied_interval_m=line['occupied_interval_m'],
                    known_weight_N=line['force_N'],state='material-projection-model-required'))
        p=fsum(_integral(r,-float('inf'),float('inf'))[0] for r in rows)
        q=fsum(_integral(r,-float('inf'),float('inf'))[1] for r in rows)
        expected=row['mass_kg']*civil.G;expected_moment=expected*(primitive['cg'][0]+row['translation_m'][0])
        if abs(p-expected)>max(1e-6,expected*1e-8) or abs(q-expected_moment)>max(1e-5,abs(expected_moment)*1e-8):
            raise ValueError('Projected source material force or first moment differs')
        segments.extend(rows);force+=expected;moment+=expected_moment
        if row['system'].startswith('wayside/'):wayside+=expected
    account_assumptions=[];unweighed=[];unassigned=[]
    if ledger is not None:
        for row in ledger['unlocated_accounts']:
            if row['system'].startswith('vehicle/'):continue
            mass=row['accounted_mass_kg']
            if mass is None:
                unweighed.append(row['id']);continue
            if type(mass) not in (int,float) or not np.isfinite(mass) or mass<0:
                raise ValueError('Finite nonnegative known account mass required')
            match=re.fullmatch(r'span/(\d+)/[^/]+',row['id'])
            if not match:
                unassigned.append(dict(id=row['id'],known_mass_kg=mass));continue
            i=int(match.group(1));a=start+i*span;b=a+span
            if a<start or b>end:raise ValueError('Named span account is outside canonical coverage')
            p=mass*civil.G
            segments.append(_uniform(a,b,p,row['id'],'unlocated-named-span-uniform-hypothesis'))
            account_assumptions.append(dict(id=row['id'],span_index=i,known_weight_N=p,
                assumed_centroid_m=(a+b)/2,actual_centroid_m=None,
                first_moment_bounds_Nm=sorted([p*a,p*b]),reaction_each_support_bounds_N=[0.,p],
                scope='Uniform for this diagnostic; actual location, distribution and installed detailing unresolved'))
            force+=p;moment+=p*(a+b)/2
    count=int(round((end-start)/span));responses=[_span_response(start+i*span,start+(i+1)*span,segments,i) for i in range(count)]
    positions=[start+i*span for i in range(count+1)];support=[0.]*(count+1)
    for i,row in enumerate(responses):support[i]+=row['left_reaction_N'];support[i+1]+=row['right_reaction_N']
    supported=fsum(row['known_dead_force_N'] for row in responses)
    supported_moment=fsum(row['known_dead_first_moment_Nm'] for row in responses)
    outside_values=[]
    for row in segments:
        if row['kind']=='point':
            if row['span_index']<0:outside_values.append((row['force_N'],row['force_N']*row['x_m']))
        else:
            outside_values.extend((_integral(row,-float('inf'),start),_integral(row,end,float('inf'))))
    outside=fsum(p for p,q in outside_values);outside_moment=fsum(q for p,q in outside_values)
    # The existing finite-axle method retains its1.3 dynamic amplification and
    # uniform accounted per-car crowd mass hypothesis; neither is acceptance.
    proxy=dict(mass=bundle['mass'],physical_definition=bundle['physical_definition'])
    offsets,axle=civil.axle_train(proxy,'crowd_control')
    live=civil.interior_pier_train_reaction(span,offsets,axle)
    def end_live():
        translations={point-a for point in (0.,span) for a in offsets}
        return max(fsum(axle*(1-(a+t)/span) for a in offsets if 0<=a+t<=span) for t in translations)
    terminal=end_live()
    supports=[dict(chainage_m=x,known_dead_reaction_N=support[i],
        conditional_crowd_train_reaction_N=terminal if i in (0,count) else live['maximum_live_reaction_N'],
        partial_combined_reaction_N=support[i]+(terminal if i in (0,count) else live['maximum_live_reaction_N']),
        complete_installed_design_reaction_N=None) for i,x in enumerate(positions)]
    result=dict(schema='osr-completion-infrastructure-loads/1',candidate_id=candidate,bundle_definition_id=bundle['definition_id'],test_only=test_only,
        scene_id=identity(scene),span_m=span,coverage_m=[start,end],span_count=count,
        dead_stock_occurrences=len(dead),known_wayside_stock_weight_N=wayside,
        known_dead_weight_N=force,known_dead_first_moment_Nm=moment,
        spans=responses,supports=supports,source_line_loads=segments,
        outside_counted_guideway_weight_N=outside,outside_counted_guideway_first_moment_Nm=outside_moment,
        force_residual_N=fsum(support)+outside-force,
        first_moment_residual_Nm=fsum(x*r for x,r in zip(positions,support))+outside_moment-moment,
        named_span_account_assumptions=account_assumptions,unsupported_projection_hypotheses=projection_hypotheses,
        equivalent_stock_projection_ids=[r['id'] for r in dead if r['scope']=='equivalent-volume-stock'],
        equivalent_stock_projection_scope='Projection is exact for the declared equivalent solid, not proof of installed rail profile, coil/end-turn placement or actual component centroid',
        unweighed_occurrence_ids=None if ledger is None else unweighed,
        unassigned_known_mass_accounts=None if ledger is None else unassigned,
        unassigned_known_weight_N=None if ledger is None else fsum(r['known_mass_kg']*civil.G for r in unassigned),
        known_dead_weight_scope='Projected material and named-span account hypotheses only; unassigned known weights are separate, unweighed equipment stays unknown',
        unlocated_account_coverage='missing-ledger' if ledger is None else 'named-span-uniform-hypotheses-plus-explicit-unknowns',
        live_axle_loads=dict(offsets_m=offsets,force_N_per_axle=axle,dynamic_factor_hypothesis=1.3,
            load_scope='Uniform accounted crowd mass per car; actual axle distribution and motor normal forces remain unqualified',
            interior_pier_influence=live),
        complete_installed_dead_load_N=None,complete_installed_pier_foundation_loads=None,
        beam_strength_buckling_torsion_fatigue_qualified=False,
        physical_scope='Known material dead loads plus declared account/axle hypotheses only. Added wayside loads require beam, prestress, bearing and substructure reevaluation.',
        source_sha256={PRODUCER:digest(__file__),civil.PRODUCER:digest(civil.__file__),geometry.PRODUCER:digest(geometry.__file__),
            railway_bundle.PRODUCER:digest(railway_bundle.__file__)},**FLAGS)
    result['evaluation_id']=identity(result)
    return result
