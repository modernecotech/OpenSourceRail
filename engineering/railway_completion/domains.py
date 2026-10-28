"""Typed, authenticated numerical closure of mechanical and economic inputs.

Authentication is supplied by the coordinator's external verifier, never by a
field in a record. Numerical support is scoped; this module issues neither a
physical acceptance nor a manufacturing or movement authority. Equipment changes
produce a physical revision proposal which must be rematerialized downstream.
"""
from copy import deepcopy
from math import exp, fsum, isfinite, sqrt
from pathlib import Path
import re

import numpy as np

from engineering.station_rail import ROOT, civil
from engineering.station_rail.common import identity, digest
from engineering.design_search import equipped_candidates
from engineering.railway_twin import geometry
from . import FLAGS

PRODUCER = 'engineering/railway_completion/domains.py'
SCHEMA = 'osr-completion-domain-record/1'
REQUIRED_SCOPES = ('installed-equipment','body-structure','independent-brakes',
                   'civil-and-site','whole-life-economics')
STRUCTURAL_SCOPES = ('normal','crowd','buckling','fatigue','joints','torsion','thermal','fire','crash')
COST_SCOPES = ('rolling-stock','guideway','stations-power','factory-tooling','construction',
               'land-utilities-depot','fleet','energy','maintenance','renewals','recovery','reliability')
UNITS = dict(length='m', mass='kg', inertia='kg*m2', force='N', stress='Pa',
             time='s', energy='J', currency='USD')


def _sha(value):
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def _number(value,name,*,positive=False,nonnegative=False):
    if type(value) not in (int,float) or not isfinite(value) or positive and value<=0 or nonnegative and value<0:
        raise ValueError('Finite '+('positive ' if positive else 'nonnegative ' if nonnegative else '')+name+' required')
    return float(value)


def _array(value,shape,name):
    raw=np.asarray(value,dtype=object)
    if raw.shape!=shape or any(type(x) not in (int,float) for x in raw.flat):
        raise ValueError('Explicit numeric '+name+' required')
    result=np.asarray(value,dtype=float)
    if not np.isfinite(result).all():raise ValueError('Finite '+name+' required')
    return result


def _refs(values,authenticated,open_items,label):
    if not isinstance(values,list) or not values or len(values)!=len(set(values)) or any(not _sha(x) for x in values):
        raise ValueError('Distinct content-bound '+label+' references required')
    missing=sorted(set(values)-authenticated)
    if missing:open_items.append(dict(kind='unauthenticated-'+label,evidence_ids=missing))


def make_record(bundle,domain,data):
    if domain not in REQUIRED_SCOPES:raise ValueError('Supported completion domain required')
    value=dict(schema=SCHEMA,domain=domain,candidate_id=bundle['candidate_id'],
        bundle_definition_id=bundle['definition_id'],body_candidate_id=bundle['body_candidate_id'],
        requirement_revision=bundle['requirement_revision'],source_sha256=deepcopy(bundle['source_sha256']),
        units=deepcopy(UNITS),data=deepcopy(data),**FLAGS)
    value['record_id']=identity(value)
    return value


def _record(record,bundle):
    expected_fields={'schema','domain','candidate_id','bundle_definition_id','body_candidate_id',
                     'requirement_revision','source_sha256','units','data','record_id',*FLAGS}
    if (not isinstance(record,dict) or record.get('schema')!=SCHEMA
        or set(record)!=expected_fields
        or record.get('record_id')!=identity({k:v for k,v in record.items() if k!='record_id'})
        or record.get('domain') not in REQUIRED_SCOPES or record.get('units')!=UNITS
        or any(record.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('Domain record schema, units, identity or release disposition differs')
    for key,expected in (('candidate_id',bundle['candidate_id']),('bundle_definition_id',bundle['definition_id']),
        ('body_candidate_id',bundle['body_candidate_id']),('requirement_revision',bundle['requirement_revision']),
        ('source_sha256',bundle['source_sha256'])):
        if record.get(key)!=expected:raise ValueError('Domain record uses another '+key)
    if not isinstance(record.get('data'),dict):raise ValueError('Typed domain data mapping required')
    def nonpromoting(value):
        if isinstance(value,dict):
            if any(key in FLAGS and item is not False for key,item in value.items()):
                raise ValueError('Nested domain inputs cannot assert physical acceptance or release')
            for item in value.values():nonpromoting(item)
        elif isinstance(value,list):
            for item in value:nonpromoting(item)
    nonpromoting(record)
    return deepcopy(record)


def _aggregate(rows):
    mass=fsum(row['mass_kg'] for row in rows)
    if mass<=0:raise ValueError('Positive installed stock mass required')
    cg=sum(row['mass_kg']*np.asarray(row['CG_m']) for row in rows)/mass
    J=np.zeros((3,3))
    for row in rows:
        d=np.asarray(row['CG_m'])-cg
        J+=np.asarray(row['CG_inertia_kg_m2'])+row['mass_kg']*((d@d)*np.eye(3)-np.outer(d,d))
    return dict(mass_kg=mass,CG_m=cg.tolist(),CG_inertia_kg_m2=J.tolist())


def _stock_inertia(part,p,rho):
    """Exact uniform-density primitive inertia, including disjoint net cuts."""
    def box_tensor(size,mass):
        x,y,z=size
        return np.diag([mass*(y*y+z*z)/12,mass*(x*x+z*z)/12,mass*(x*x+y*y)/12])
    def cylinder_tensor(radius,inner,length,mass,axis):
        axial=mass*(radius*radius+inner*inner)/2
        transverse=mass*(3*(radius*radius+inner*inner)+length*length)/12
        return transverse*np.eye(3)+(axial-transverse)*np.outer(axis,axis)
    if part['kind']=='oriented-RHS':
        w,h,t,L=(p[k] for k in ('width','height','wall','length'))
        local=box_tensor([w,h,L],rho*w*h*L)-box_tensor([w-2*t,h-2*t,L],rho*(w-2*t)*(h-2*t)*L)
        return p['basis']@local@p['basis'].T
    if part['kind'] in ('cylinder','annular-cylinder'):
        return cylinder_tensor(p['radius'],p['inner'],p['length'],rho*p['volume'],p['basis'][:,2])
    size=np.asarray(part['size_m']);cg=np.asarray(part['at_m'])+size/2
    full_mass=rho*float(np.prod(size));delta=cg-p['cg']
    tensor=box_tensor(size,full_mass)+full_mass*((delta@delta)*np.eye(3)-np.outer(delta,delta))
    for cut in p['voids']:
        mass=rho*cut['volume'];delta=cut['cg']-p['cg']
        central=box_tensor(cut['size'],mass) if cut['kind']=='box' else cylinder_tensor(cut['radius'],0.,cut['length'],mass,cut['axis'])
        tensor-=central+mass*((delta@delta)*np.eye(3)-np.outer(delta,delta))
    return tensor


def _installed(data,bundle,body,ledger,authenticated):
    """Evaluate a fully enumerated replacement train, never mutate its parent."""
    open_items=[];checks=[];scene=ledger.get('scene',ledger.get('base_scene'))
    if scene is None:
        return dict(open_items=[dict(kind='missing-base-scene')],checks=[],proposal=None)
    if scene.get('candidate_id')!=bundle['candidate_id'] or data.get('base_scene_id')!=identity(scene):
        raise ValueError('Installed proposal uses another exact base scene')
    base={r['id']:r for r in scene['occurrences'] if r['system'].startswith('vehicle/')}
    accounts={r['id']:r for r in ledger['unlocated_accounts'] if r['system'].startswith('vehicle/')}
    removed=data.get('remove_occurrence_ids')
    if not isinstance(removed,list) or len(removed)!=len(set(removed)) or not set(removed)<=set(base)|set(accounts):
        raise ValueError('Explicit disjoint existing stock/account removal IDs required')
    if set(removed)!=set(base)|set(accounts):
        open_items.append(dict(kind='unresolved-parent-vehicle-occurrences',occurrence_ids=sorted((set(base)|set(accounts))-set(removed))))
    rows=data.get('net_occurrences')
    if not isinstance(rows,list) or not rows or len(rows)>50000:raise ValueError('Bounded actual net-component list required')
    ids=[r.get('id') for r in rows]
    if any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):
        raise ValueError('Unique proposed physical occurrence IDs required')
    properties=[];car_rows={i:[] for i in range(6)};hardware_counts={k:0 for k in equipped_candidates.HARDWARE_KINDS}
    for row in rows:
        if type(row.get('car_index')) is not int or row['car_index'] not in car_rows:
            raise ValueError('Explicit six-car occurrence assignment required')
        part=row.get('geometry')
        if not isinstance(part,dict):raise ValueError('Actual component net geometry required')
        # The stock primitive verifier derives volume/centroid, not just a saved
        # box or mass claim. Arbitrary opaque native geometry is not admitted.
        primitive=geometry._primitive(part)
        rho=_number(row.get('density_kg_m3'),'component density',positive=True)
        mass=primitive['volume']*rho
        nominal=_number(row.get('mass_kg'),'component mass',positive=True)
        if abs(mass-nominal)>max(1e-8,mass*1e-7):raise ValueError('Net geometry/density and component mass differ')
        interval=_array(row.get('mass_interval_kg'),(2,),'component mass interval')
        if not 0<interval[0]<=mass<=interval[1]:raise ValueError('Positive mass bounds must contain derived component mass')
        R,t=equipped_candidates.transform(row['installed_transform'])
        local_cg=_array(row.get('local_CG_m'),(3,),'component local CG')
        if not np.allclose(local_cg,primitive['cg'],atol=1e-8,rtol=0):raise ValueError('Component CG differs from actual net geometry')
        J=equipped_candidates._inertia(row['local_CG_inertia_kg_m2'])
        derived=_stock_inertia(part,primitive,rho)
        if not np.allclose(J,derived,rtol=1e-7,atol=1e-8):
            raise ValueError('Component inertia differs from actual net geometry and density')
        covariance=np.trace(J)/2*np.eye(3)-J
        if np.any(np.diag(covariance)>mass*(primitive['hi']-local_cg)*(local_cg-primitive['lo'])+1e-8):
            raise ValueError('Component inertia exceeds its occupied geometry envelope')
        if not _sha(row.get('component_definition_id')) or row['component_definition_id']!=identity(part):
            raise ValueError('Proposed component definition must identify actual geometry')
        _refs(row.get('source_evidence_ids'),authenticated,open_items,'component-source')
        if not isinstance(row.get('origin_country'),str) or not row['origin_country']:
            open_items.append(dict(kind='untraced-component-origin',occurrence_id=row['id']))
        subordinate=row.get('hardware_and_services')
        if not isinstance(subordinate,list):raise ValueError('Counted subordinate hardware/services required')
        subids=set();submass=0.
        for item in subordinate:
            if item.get('id') in subids or not isinstance(item.get('id'),str) or item.get('kind') not in hardware_counts:
                raise ValueError('Distinct typed subordinate hardware/service occurrences required')
            subids.add(item['id']);quantity=item.get('quantity')
            if type(quantity) is not int or quantity<=0:raise ValueError('Positive hardware count required')
            positions=_array(item.get('positions_local_m'),(quantity,3),'hardware positions')
            if np.any(positions<primitive['lo']) or np.any(positions>primitive['hi']):raise ValueError('Hardware lies outside the component')
            included=_number(item.get('included_mass_kg'),'included hardware mass',positive=True);submass+=included
            hardware_counts[item['kind']]+=quantity
            if item['kind'] in ('wire','hose','duct','cooling'):
                radius=_number(item.get('minimum_bend_radius_m'),'minimum bend radius',positive=True)
                actual=_number(item.get('installed_bend_radius_m'),'installed bend radius',positive=True)
                slack=_number(item.get('provided_slack_m'),'provided flexibility slack',nonnegative=True)
                required=_number(item.get('required_motion_slack_m'),'required motion slack',nonnegative=True)
                checks.append(dict(id=row['id']+'/'+item['id']+'/flexibility',pass_=actual>=radius and slack>=required,
                    bend_margin_m=actual-radius,slack_margin_m=slack-required))
                _refs(item.get('duty_evidence_ids'),authenticated,open_items,'flexibility-duty')
        if submass>mass+1e-8:raise ValueError('Inclusive hardware mass exceeds component mass')
        access=row.get('access',{})
        for key,endpoint in (('installation_path',-1),('removal_path',0)):
            path=access.get(key)
            if not isinstance(path,list) or not path or path[endpoint]!=row['installed_transform']:
                raise ValueError('Assembly access path must meet its actual installed pose')
            sweep=equipped_candidates.swept_envelope(dict(min_m=primitive['lo'].tolist(),max_m=primitive['hi'].tolist()),path)
            for obstacle in access.get('obstacles_vehicle_m',[]):
                lo,hi=equipped_candidates._box(obstacle)
                intersects=bool(np.all(np.asarray(sweep['max_m'])>lo)&np.all(np.asarray(sweep['min_m'])<hi))
                checks.append(dict(id=row['id']+'/'+key+'/obstacle',pass_=not intersects,
                    scope='Conservative swept-bound intersection; false positives require refined collision analysis'))
        if not access.get('tool_envelopes') or not access.get('sequence'):
            open_items.append(dict(kind='missing-tool-or-installation-sequence',occurrence_id=row['id']))
        for bounds in access.get('tool_envelopes',[]):equipped_candidates._box(bounds)
        rated=_number(access.get('lifting_capacity_kg'),'lifting capacity',positive=True)
        checks.append(dict(id=row['id']+'/lift',pass_=rated>=interval[1],margin_kg=rated-interval[1]))
        _refs(access.get('inspection_retention_evidence_ids'),authenticated,open_items,'retention-access')
        value=dict(id=row['id'],mass_kg=mass,CG_m=(R@local_cg+t).tolist(),CG_inertia_kg_m2=(R@J@R.T).tolist())
        car_rows[row['car_index']].append(value)
        train_value=deepcopy(value)
        train_value['CG_m']=(np.asarray(value['CG_m'])+[-8.5-17.5*row['car_index'],0.,0.]).tolist()
        properties.append(train_value)
    if any(not items for items in car_rows.values()):open_items.append(dict(kind='missing-equipped-car'))
    operations=data.get('net_stock_operations')
    if not isinstance(operations,list):raise ValueError('Explicit gross-to-net stock operations required')
    parents=[r.get('parent_occurrence_id') for r in operations]
    if len(parents)!=len(set(parents)) or not set(parents)<=set(base):raise ValueError('Disjoint original stock operation binding required')
    if set(parents)!=set(base):open_items.append(dict(kind='unresolved-gross-stock-cuts',occurrence_ids=sorted(set(base)-set(parents))))
    referenced=set();stock_targets=set();net_by_id={r['id']:r for r in rows}
    for operation in operations:
        original=base[operation['parent_occurrence_id']]
        if operation.get('parent_geometry_id')!=identity(original['geometry']):raise ValueError('Gross-to-net source geometry differs')
        targets=operation.get('replacement_occurrence_ids')
        if not isinstance(targets,list) or not targets or not set(targets)<=set(ids):raise ValueError('Actual net replacement occurrence references required')
        if stock_targets.intersection(targets):raise ValueError('Net stock replacement counted against more than one source blank')
        stock_targets.update(targets)
        volume=fsum(geometry._primitive(net_by_id[key]['geometry'])['volume'] for key in targets)
        removed_volume=_number(operation.get('removed_volume_m3'),'actual stock cut volume',nonnegative=True)
        residual=original['geometry']['volume_m3']-volume-removed_volume
        if abs(residual)>max(1e-10,original['geometry']['volume_m3']*1e-7):
            raise ValueError('Gross-to-net cut volume does not reconcile')
        checks.append(dict(id=operation['parent_occurrence_id']+'/net-volume',pass_=True,residual_m3=residual))
        referenced.update(targets)
        _refs(operation.get('cut_joint_clearance_evidence_ids'),authenticated,open_items,'net-stock-cut-and-clearance')
    # Extra hardware need not originate in a body blank, but each must explicitly
    # discharge a removed account/joint rather than appear as untracked mass.
    discharged=data.get('account_resolution')
    if not isinstance(discharged,list):raise ValueError('Actual parent-account resolution mapping required')
    account_ids=[r.get('parent_account_id') for r in discharged]
    if len(account_ids)!=len(set(account_ids)) or not set(account_ids)<=set(accounts):raise ValueError('Unique existing account resolutions required')
    if set(account_ids)!=set(accounts):open_items.append(dict(kind='unresolved-parent-accounts',occurrence_ids=sorted(set(accounts)-set(account_ids))))
    for row in discharged:
        if not isinstance(row.get('replacement_occurrence_ids'),list) or not set(row['replacement_occurrence_ids'])<=set(ids):
            raise ValueError('Actual account replacement geometry references required')
        if not row['replacement_occurrence_ids']:
            _refs(row.get('absence_or_no_residual_evidence_ids'),authenticated,open_items,'discharged-zero-residual')
        referenced.update(row['replacement_occurrence_ids'])
    if referenced!=set(ids):open_items.append(dict(kind='unassigned-proposed-occurrences',occurrence_ids=sorted(set(ids)-referenced)))
    physical=dict(parent_candidate_id=bundle['candidate_id'],remove_occurrence_ids=removed,
        net_occurrences=deepcopy(rows),net_stock_operations=deepcopy(operations),account_resolution=deepcopy(discharged))
    aggregate=_aggregate(properties)
    return dict(open_items=open_items,checks=checks,proposed_physical_definition_revision=physical,
        proposed_physical_revision_id=identity(physical),replacement_rows=properties,hardware_counts=hardware_counts,
        hardware_count_scope='Submitted subordinate occurrences only; zero is no observed count, not proof of absent installed hardware',
        complete_installed_hardware_counts=None,
        proposed_train_mass_properties=aggregate,
        proposed_per_car_mass_properties={str(i):_aggregate(items) if items else None for i,items in car_rows.items()},
        coordinate_frames=dict(vehicle='Per-car center; x longitudinal/y left/z up',train='Initial leading nose at0; car centers -8.5-17.5*i m'),
        canonical_rematerialization_required=True,
        parent_mass_must_not_be_overwritten=True,complete_installed_mass_kg=None,
        proposed_installed_mass_kg=aggregate['mass_kg'] if not open_items else None,
        physical_closure_open=['Native net geometry and full interference/tolerance confirmation','Retention, lifting load-sharing, structural and physical qualification'])


def _structure(data,bundle,body,ledger,authenticated):
    open_items=[];checks=[];rows=data.get('results')
    if not isinstance(rows,list) or not 1<=len(rows)<=256:raise ValueError('Bounded actual structural numerical results required')
    present={r.get('scope') for r in rows}
    if not present<=set(STRUCTURAL_SCOPES):raise ValueError('Explicit structural scope required')
    for scope in sorted(set(STRUCTURAL_SCOPES)-present):open_items.append(dict(kind='missing-structural-scope',scope=scope))
    for row in rows:
        load=row.get('load')
        if load not in ('normal','crowd'):raise ValueError('Explicit structural passenger load required')
        if row['scope'] in ('normal','crowd') and load!=row['scope']:
            raise ValueError('Structural scope and passenger load differ')
        expected=bundle['mass']['accounted_cap_loaded_kg_per_car' if load=='normal' else 'accounted_160_control_kg_per_car']
        if row.get('applied_mass_kg_per_car')!=expected:raise ValueError('Structural load uses another mass scope')
        if row.get('unit') not in ('Pa','m','N','1','K','cycle'):raise ValueError('Typed structural observable units required')
        fine=_number(row.get('fine'),'refined structural observable');coarse=_number(row.get('coarse'),'coarse structural observable')
        uncertainty=_number(row.get('uncertainty'),'structural uncertainty',nonnegative=True)
        limit=_number(row.get('limit'),'structural limit',positive=True)
        tolerance=_number(row.get('convergence_limit_fraction'),'declared numerical refinement tolerance',positive=True)
        if tolerance>.25:raise ValueError('Refinement tolerance outside this numerical reporting domain')
        meshes=row.get('mesh_ids')
        if not isinstance(meshes,list) or len(meshes)!=2 or meshes[0]==meshes[1] or any(not _sha(x) for x in meshes):
            raise ValueError('Two distinct actual mesh identities required')
        _refs(row.get('raw_result_ids'),authenticated,open_items,'structural-result')
        _refs([row.get('criterion_record_id')],authenticated,open_items,'structural-criterion')
        change=abs(fine-coarse)/max(abs(fine),1e-12)
        comparison=row.get('comparison')
        if comparison not in ('le','ge'):raise ValueError('Supported structural comparison required')
        guarded=fine+uncertainty if comparison=='le' else fine-uncertainty
        margin=limit-guarded if comparison=='le' else guarded-limit
        checks.append(dict(id=row['scope'],pass_=margin>=0 and change<=tolerance,
            guard_banded_observable=guarded,margin=margin,unit=row['unit'],relative_refinement_change=change,
            convergence_margin=tolerance-change))
    return dict(open_items=open_items,checks=checks,physical_closure_open=['Material/joint lots, applicable approved load basis and physical correlation remain independently reviewed'])


def _brakes(data,bundle,body,ledger,authenticated):
    open_items=[];checks=[];results=[];cases=data.get('cases')
    if not isinstance(cases,list) or not cases or len(cases)>24:raise ValueError('Bounded independent braking cases required')
    required={'empty','normal','crowd','wet','hot','lost-channel','parking'}
    missing=required-{r.get('name') for r in cases}
    open_items += [dict(kind='missing-brake-case',name=n) for n in sorted(missing)]
    for row in cases:
        load=row.get('load')
        if load not in ('empty','normal','crowd'):raise ValueError('Explicit braking load required')
        mass=bundle['mass'][{'empty':'accounted_tare_kg_per_car','normal':'accounted_cap_loaded_kg_per_car','crowd':'accounted_160_control_kg_per_car'}[load]]
        if row.get('brake_definition_id')!=bundle['brake_definition']['brake_definition_id']:
            raise ValueError('Brake hardware definition differs')
        _refs(row.get('force_evidence_ids'),authenticated,open_items,'brake-force')
        _refs([row.get('criterion_record_id')],authenticated,open_items,'brake-criterion')
        v=_number(row.get('initial_speed_m_s'),'brake entry speed',nonnegative=True)
        grade=_number(row.get('grade_up_fraction'),'braking grade')
        if abs(grade)>.1 or v>40:raise ValueError('Braking hypothesis outside numerical domain')
        adhesion=_number(row.get('adhesion'),'rail adhesion',positive=True)
        dt=_number(row.get('dt_s'),'brake integration step',positive=True)
        horizon=_number(row.get('horizon_s'),'brake observation horizon',positive=True)
        if dt>.1 or horizon>600 or horizon/dt>24000:raise ValueError('Braking numerical execution budget exceeded')
        samples=row.get('force_curve')
        if not isinstance(samples,list) or len(samples)<2:raise ValueError('Measured/verified force-time curve required')
        times=[_number(s['time_s'],'force sample time',nonnegative=True) for s in samples]
        forces=[_number(s['force_N_per_car'],'force sample',nonnegative=True) for s in samples]
        if times[0]!=0 or times[-1]<horizon or any(b<=a for a,b in zip(times,times[1:])):
            raise ValueError('Brake force-time samples must cover the whole case without extrapolation')
        effective=mass+bundle['rotating_equivalent_kg_per_car'];normal=mass*civil.G/sqrt(1+grade*grade)
        gravity=-mass*civil.G*grade/sqrt(1+grade*grade);initial=.5*effective*v*v
        x=t=heat=gravity_work=0.;stopped=v==0
        while t<horizon-1e-10:
            h=min(dt,horizon-t);force=min(float(np.interp(t+h/2,times,forces)),adhesion*normal)
            if v==0:
                if abs(gravity)<=force:stopped=True;break
                stopped=False;break
            acceleration=(gravity-force)/effective
            if acceleration<0 and v+acceleration*h<0:h=-v/acceleration
            newv=max(0.,v+acceleration*h);dx=(v+newv)*h/2
            x+=dx;t+=h;heat+=force*dx;gravity_work+=gravity*dx;v=newv
            if v<=1e-9:stopped=True;break
        distance_limit=_number(row.get('stop_distance_limit_m'),'approved stop distance',positive=True)
        capacity=_number(row.get('disc_heat_capacity_J_K_per_car'),'installed disc heat capacity',positive=True)
        ambient=_number(row.get('ambient_C'),'brake ambient');maximum=_number(row.get('maximum_disc_C'),'brake thermal limit')
        cooling=_number(row.get('heat_rejection_W_K_per_car'),'brake heat rejection',positive=True)
        period=_number(row.get('brake_cycle_s'),'vehicle brake repeat period',positive=True)
        _refs(row.get('thermal_duty_evidence_ids'),authenticated,open_items,'brake-thermal-duty')
        peak=ambient+(heat/capacity)/(1-exp(-cooling*period/capacity))
        residual=initial+gravity_work-heat-.5*effective*v*v
        checks.append(dict(id=row['name'],pass_=stopped and x<=distance_limit and peak<=maximum,
            stopping_margin_m=distance_limit-x,thermal_margin_C=maximum-peak))
        results.append(dict(name=row['name'],stopped=stopped,distance_m=x,time_s=t,final_speed_m_s=v,
            heat_J_per_car=heat,energy_residual_J_per_car=residual,periodic_impulse_temperature_bound_C=peak,
            thermal_scope='Lumped impulse-heat/cooling recurrence; actual fade/WSP/protection require independent correlation'))
    return dict(open_items=open_items,checks=checks,cases=results,
        physical_closure_open=['Installed independent supply, localisation, brake latency, WSP, fade, protection and rescue qualification'])


def _civil(data,bundle,body,ledger,authenticated):
    open_items=[];checks=[];results=[]
    route=bundle['architecture_case']['physical_definition']['route']
    _refs(data.get('site_evidence_ids'),authenticated,open_items,'site-geotechnical')
    supports=data.get('supports')
    if not isinstance(supports,list) or len(supports)<2 or len(supports)>1000:raise ValueError('Actual bounded support stationing required')
    positions=[_number(r['chainage_m'],'support chainage') for r in supports]
    if positions[0]!=route['counted_guideway_start_m'] or positions[-1]!=route['counted_guideway_end_m'] or any(abs(b-a-20)>1e-8 for a,b in zip(positions,positions[1:])):
        raise ValueError('Support stationing differs from canonical span/route geometry')
    selected=civil.alternative(dict(mass=bundle['mass'],physical_definition=bundle['physical_definition']),20.,'box-beam','crowd_control')
    offsets,axle=civil.axle_train(dict(mass=bundle['mass'],physical_definition=bundle['physical_definition']),'crowd_control')
    fractions=[_number(r.get('braking_distribution_fraction'),'braking distribution fraction',nonnegative=True) for r in supports]
    if any(x>1 for x in fractions) or abs(fsum(fractions)-1)>1e-9:raise ValueError('Conservative complete braking-force distribution required')
    for i,row in enumerate(supports):
        center=positions[i];left=positions[i-1] if i else center;right=positions[i+1] if i+1<len(positions) else center
        def influence(x):
            if x<center:return (x-left)/(center-left) if left<=x and left<center else 0.
            return (right-x)/(right-center) if x<=right and right>center else float(x==center)
        translations={point-a for point in (left,center,right) for a in offsets}
        live=max(fsum(axle*max(0.,influence(a+t)) for a in offsets) for t in translations)
        super_dead=selected['total_counted_span_mass_kg']*civil.G*((int(i>0)+int(i+1<len(positions)))/2)
        _refs(row.get('load_and_geometry_evidence_ids'),authenticated,open_items,'foundation-load-geometry')
        L=_number(row.get('footing_length_m'),'footing length',positive=True);B=_number(row.get('footing_width_m'),'footing width',positive=True)
        depth=_number(row.get('footing_depth_m'),'footing depth',positive=True)
        rho=_number(row.get('concrete_density_kg_m3'),'foundation concrete density',positive=True)
        pier_volume=_number(row.get('pier_headstock_volume_m3'),'pier/headstock volume',positive=True)
        extra=_number(row.get('other_vertical_load_N'),'other actual vertical load',nonnegative=True)
        vertical=live+super_dead+(L*B*depth+pier_volume)*rho*civil.G+extra
        Mx=_number(row.get('overturning_Mx_Nm'),'foundation moment x');My=_number(row.get('overturning_My_Nm'),'foundation moment y')
        horizontal=max(_number(row.get('horizontal_load_N'),'foundation horizontal force',nonnegative=True),
            6*bundle['mass']['accounted_160_control_kg_per_car']*.6*fractions[i])
        bearing=_number(row.get('allowable_bearing_Pa'),'site allowable bearing',positive=True)
        mu=_number(row.get('base_friction_coefficient'),'foundation base friction',positive=True)
        sliding_factor=_number(row.get('minimum_sliding_factor'),'declared sliding factor',positive=True)
        if sliding_factor<1:raise ValueError('Sliding necessary bound cannot permit force imbalance')
        q=vertical/(L*B);delta=6*abs(Mx)/(L*B*B)+6*abs(My)/(B*L*L);qmax=q+delta;qmin=q-delta
        E=_number(row.get('soil_elastic_modulus_Pa'),'site soil modulus',positive=True);nu=_number(row.get('soil_poisson'),'site Poisson ratio')
        if not -1<nu<.5:raise ValueError('Physical soil elastic Poisson ratio required')
        shape=_number(row.get('settlement_shape_factor'),'settlement shape factor',positive=True)
        settlement=q*B*(1-nu*nu)/E*shape
        settlement_limit=_number(row.get('settlement_limit_m'),'approved settlement limit',positive=True)
        checks.append(dict(id=row['id'],pass_=qmax<=bearing and qmin>=0 and horizontal*sliding_factor<=mu*vertical and settlement<=settlement_limit,
            bearing_margin_Pa=bearing-qmax,contact_margin_Pa=qmin,sliding_margin_N=mu*vertical-horizontal*sliding_factor,
            settlement_margin_m=settlement_limit-settlement))
        results.append(dict(id=row['id'],maximum_train_reaction_N=live,counted_superstructure_dead_reaction_N=super_dead,
            design_vertical_reaction_N=vertical,qmax_Pa=qmax,qmin_Pa=qmin,elastic_settlement_m=settlement,
            footing_concrete_m3=L*B*depth,pier_headstock_concrete_m3=pier_volume))
    physical=dict(parent_candidate_id=bundle['candidate_id'],supports=deepcopy(supports),
        site_evidence_ids=deepcopy(data['site_evidence_ids']))
    return dict(open_items=open_items,checks=checks,supports=results,
        proposed_civil_physical_definition=physical,proposed_civil_revision_id=identity(physical),canonical_rematerialization_required=True,
        source_civil_component_id=selected['physical_civil_component_id'],
        physical_closure_open=['Simple-span and elastic shallow-footing numerical scope only; seismic, lateral system, flood/scour, liquefaction, piles and erection remain separate obligations'])


def _economics(data,bundle,body,ledger,authenticated):
    open_items=[];checks=[];scene=ledger.get('scene',ledger.get('base_scene'))
    if scene is None:return dict(open_items=[dict(kind='missing-costed-scene')],checks=[],whole_life_cost_USD=None)
    expected={r['id'] for r in scene['occurrences']}|{r['id'] for r in ledger['unlocated_accounts']}
    physical={r['id']:r for r in scene['occurrences']}
    accounts={r['id']:r for r in ledger['unlocated_accounts']}
    rows=data.get('quotes')
    if not isinstance(rows,list):raise ValueError('Explicit quote occurrences required')
    ids=[r.get('occurrence_id') for r in rows]
    if len(ids)!=len(set(ids)) or not set(ids)<=expected:raise ValueError('Quotes must cover distinct actual canonical occurrences')
    missing=sorted(expected-set(ids))
    if missing:open_items.append(dict(kind='unpriced-canonical-occurrences',occurrence_ids=missing))
    known=[]
    for row in rows:
        if row.get('currency')!='USD' or row.get('unit') not in ('occurrence','kg','m','m3','assembly'):
            raise ValueError('Explicit quote currency and quantity unit required')
        quantity=row.get('quantity');price=row.get('unit_price_USD')
        if quantity is None or price is None:
            open_items.append(dict(kind='unknown-quoted-quantity-or-price',occurrence_id=row['occurrence_id']));continue
        quantity=_number(quantity,'quoted quantity',positive=True);price=_number(price,'quote unit price',nonnegative=True)
        occurrence=physical.get(row['occurrence_id'],accounts.get(row['occurrence_id']))
        if row.get('component_definition_id')!=occurrence.get('component_definition_id'):
            raise ValueError('Quote physical component definition differs')
        unit=row['unit'];needed=None
        if row['occurrence_id'] in physical:
            part=occurrence['geometry']
            if unit=='occurrence':needed=1.
            elif unit=='kg':needed=occurrence['mass_kg']
            elif unit=='m3':needed=part['volume_m3']
            elif unit=='m' and part['kind']=='oriented-RHS':needed=float(np.linalg.norm(np.asarray(part['end_m'])-part['start_m']))
            elif unit=='m' and 'length_m' in part:needed=part['length_m']
        if needed is None:open_items.append(dict(kind='unresolved-quote-unit-or-component',occurrence_id=row['occurrence_id']))
        elif quantity+1e-9<needed:raise ValueError('Quoted quantity does not cover the canonical component')
        _refs([row.get('quote_evidence_id')],authenticated,open_items,'supplier-quote')
        if not isinstance(row.get('origin_country'),str) or not row['origin_country']:
            open_items.append(dict(kind='untraced-price-origin',occurrence_id=row['occurrence_id']))
        known.append(quantity*price)
    scopes=data.get('scope_costs')
    if not isinstance(scopes,list):raise ValueError('Whole-system service scope costs required')
    scope_names=[r.get('scope') for r in scopes]
    if len(scope_names)!=len(set(scope_names)) or not set(scope_names)<=set(COST_SCOPES):raise ValueError('Unique known whole-life cost scopes required')
    for scope in sorted(set(COST_SCOPES)-set(scope_names)):open_items.append(dict(kind='missing-whole-system-cost-scope',scope=scope))
    years=data.get('design_life_years')
    if type(years) is not int or not 1<=years<=100:raise ValueError('Bounded whole-life design years required')
    discount=_number(data.get('real_discount_rate'),'real discount rate')
    if not -.1<discount<.5:raise ValueError('Discounting model domain exceeded')
    context=dict(cars=bundle['cars'],normal_people_per_car=46,headway_s=120.,
        station_spacing_m=bundle['architecture_case']['physical_definition']['route']['station_spacing_m'])
    if data.get('service_context')!=context:raise ValueError('Economic service comparison context differs')
    cashflows=[];scope_total=0.
    for scope in scopes:
        _refs(scope.get('evidence_ids'),authenticated,open_items,'whole-system-cost')
        for row in scope.get('cashflows',[]):
            year=row.get('year');value=row.get('cost_USD')
            if type(year) is not int or not 0<=year<=years:raise ValueError('Cashflow year outside design life')
            if value is None:open_items.append(dict(kind='unknown-lifecycle-cost',scope=scope['scope'],year=year));continue
            cost=_number(value,'whole-life cashflow',nonnegative=True);present=cost/(1+discount)**year
            cashflows.append(dict(scope=scope['scope'],year=year,cost_USD=cost,present_cost_USD=present));scope_total+=present
        if not scope.get('cashflows'):open_items.append(dict(kind='missing-lifecycle-cashflows',scope=scope['scope']))
    # Canonical occurrence quotes constitute the stock CAPEX. Each other scope
    # must explicitly exclude these lines; otherwise it would double count them.
    if data.get('scope_costs_exclude_occurrence_quotes') is not True:
        raise ValueError('Disjoint stock and additional whole-system cost scopes required')
    stock=fsum(known);total=stock+scope_total
    unresolved=[r['id'] for r in ledger['unlocated_accounts']]
    if unresolved:open_items.append(dict(kind='unresolved-installed-physical-cost-scope',occurrence_ids=unresolved))
    checks.append(dict(id='known-cashflow-reconciliation',pass_=abs(total-stock-fsum(r['present_cost_USD'] for r in cashflows))<=max(1e-6,total*1e-12),
        residual_USD=total-stock-fsum(r['present_cost_USD'] for r in cashflows)))
    return dict(open_items=open_items,checks=checks,known_quoted_stock_subtotal_USD=stock if known else None,
        known_additional_lifecycle_present_cost_USD=scope_total if cashflows else None,cashflows=cashflows,
        conditional_whole_life_cost_USD=total if not open_items else None,whole_life_cost_USD=None,economic_winner=None,
        physical_closure_open=['Protected equal-service operation and complete installed supply/manufacturing/site scope required before economic selection'])


HANDLERS={'installed-equipment':_installed,'body-structure':_structure,'independent-brakes':_brakes,
          'civil-and-site':_civil,'whole-life-economics':_economics}


def evaluate(bundle,body,ledger,records=(),authenticated=(),*,root=ROOT):
    """Recompute supplied domain arithmetic under exact parent identities.

    ``authenticated`` must come from the coordinator's external verifier. A
    caller can exercise this pure numerical adapter with fixtures; doing so does
    not authenticate a real record or authorize hardware. Nonempty approved
    physical records may propose a new assembly, never silently change this one.
    """
    if (body.get('candidate_id')!=bundle.get('body_candidate_id')
        or ledger.get('candidate_id')!=bundle.get('candidate_id')):
        raise ValueError('Mixed body, ledger and canonical bundle identities')
    trusted=set(authenticated)
    if any(not _sha(x) for x in trusted):raise ValueError('Authenticated content identities required')
    normalized=[_record(r,bundle) for r in records]
    if len({r['domain'] for r in normalized})!=len(normalized):
        raise ValueError('Select one exact record per domain before evaluation')
    by_domain={r['domain']:r for r in normalized};outputs={}
    for domain in REQUIRED_SCOPES:
        record=by_domain.get(domain)
        if record is None or record['record_id'] not in trusted:
            outputs[domain]=dict(state='missing',evidence_ids=[],numeric_residuals={},
                open_items=[dict(kind='missing-authenticated-domain-input',record_id=None if record is None else record['record_id'])],**FLAGS)
            continue
        value=HANDLERS[domain](record['data'],bundle,body,ledger,trusted)
        for check in value['checks']:
            check['pass_']=bool(check['pass_'])
        failed=[r for r in value['checks'] if r['pass_'] is not True]
        value.update(state='fail' if failed else 'missing' if value['open_items'] else 'supported-for-numerical-scope',
            evidence_ids=[record['record_id']],numeric_residuals={r['id']:r for r in value['checks']},**FLAGS)
        outputs[domain]=value
    producers=((PRODUCER,Path(__file__)),(geometry.PRODUCER,Path(geometry.__file__)),
        (equipped_candidates.PRODUCER,Path(equipped_candidates.__file__)),(civil.PRODUCER,Path(civil.__file__)))
    source_map={}
    for name,loaded in producers:
        source_map[name]=digest(Path(root)/name)
        if source_map[name]!=digest(loaded):raise ValueError('Executing domain dependency differs from source root')
    result=dict(schema='osr-completion-domain-evaluation/1',candidate_id=bundle['candidate_id'],
        bundle_definition_id=bundle['definition_id'],body_candidate_id=body['candidate_id'],
        record_ids=[r['record_id'] for r in normalized],domains=outputs,
        numerical_domains_supported=sum(r['state']=='supported-for-numerical-scope' for r in outputs.values()),
        source_sha256=source_map,
        physical_completion=False,**FLAGS)
    result['evaluation_id']=identity(result)
    return result
