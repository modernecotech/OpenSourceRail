"""Candidate-bound, equilibrium-led structural design study.

This is a calculated design package, not engineering acceptance. Material limits,
load combinations and soil resistances are explicit study inputs. Changed stock
is an alternative requiring a new common candidate and a repeated dynamic run.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import math
import tomllib
import gzip
import io

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('candidate-structures.toml')
DATA=Path(__file__).with_name('data')
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_candidate_structures.py'
SCHEMA='osr-candidate-structural-study/1'
FLAGS=dict(design_complete=False,physical_validation=False,manufacturing_release=False,
           physical_release=False,engineering_accepted=False,automatic_adoption=False)
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/candidate-structures'
MAX_RAW=64*1024*1024
FILES={'study.json.gz','load-envelope.json.gz','geometry.json.gz','bom.json','beam-section.svg','candidate-load-plan.svg','overview.svg','section.png','README.md'}


def encoded(value):
    def scalar(v):
        if isinstance(v,np.generic):return v.item()
        raise TypeError(f'Unsupported structural payload type: {type(v).__name__}')
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False,default=scalar).encode()


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-candidate-structural-input/1' or any(a[k] is not False for k in ('engineering_accepted','site_accepted','automatic_adoption')):
        raise ValueError('unqualified structural study inputs required')
    if a['concrete']['span_m']!=25 or a['loads']['train_cars']!=6:
        raise ValueError('explicit six-car/25m study boundary required')
    return a


def source_paths():
    from . import candidate_magnetics
    return sorted({Path(__file__),INPUT,TEST,*candidate_magnetics.source_paths(),
        DATA/'candidate-retained-body-stock.json',DATA/'candidate-replaced-cartridges.json',
        DATA/'candidate-protection-equipment.json',DATA/'candidate-parent-94ad.json',DATA/'candidate-attachment-equipment.json',
        ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/site-context.json'})


def _finite(value):
    return type(value) in (int,float) and math.isfinite(value)


def _box(size,at):
    v=math.prod(size);c=np.asarray(at,dtype=float)+np.asarray(size)/2
    return v,c,np.diag([v*sum(size[k]**2 for k in range(3) if k!=i)/12 for i in range(3)])


def primitive(part):
    """Independent signed box/cylinder integrals, including drilled holes."""
    at=np.asarray(part['at_m'],dtype=float);size=part['size_m']
    def cylinder(d,h,p,axis):
        v=math.pi*d*d*h/4;c=np.asarray(p,dtype=float).copy();c[axis]+=h/2
        return v,c,np.diag([v*(d*d/8 if i==axis else (3*d*d/4+h*h)/12) for i in range(3)])
    if part['kind']=='box':pieces=[(1,_box(size,at))]
    elif part['kind']=='cylinder':
        axis='xyz'.index(part.get('cylinder_axis','z'));p=at.copy()
        for i in range(3):
            if i!=axis:p[i]+=size[0]/2
        pieces=[(1,cylinder(size[0],size[2],p,axis))]
    else:raise ValueError('known solid box/cylinder primitive required')
    for hole in part.get('holes',[]):
        axis='xyz'.index(hole.get('axis','z'));p=at.copy()
        for i in range(3):p[i]+=hole.get('start_m',0) if i==axis else hole['xyz'[i]+'_m']
        run=hole.get('length_m',size[axis] if part['kind']=='box' else size[2])
        pieces.append((-1,cylinder(hole['diameter_m'],run,p,axis)))
    v=math.fsum(sign*x[0] for sign,x in pieces)
    if not v>0:raise ValueError('nonpositive material region')
    c=sum(sign*x[0]*x[1] for sign,x in pieces)/v;I=np.zeros((3,3))
    for sign,(vol,centre,local) in pieces:
        r=centre-c;I+=sign*(local+vol*(np.dot(r,r)*np.eye(3)-np.outer(r,r)))
    if np.linalg.eigvalsh(I).min()<-1e-9:raise ValueError('invalid signed primitive inertia')
    return v,c,I


def _combine(regions):
    mass=math.fsum(r['mass_kg'] for r in regions)
    if mass<=0:raise ValueError('positive mass required')
    cg=sum(r['mass_kg']*np.asarray(r['cg_m']) for r in regions)/mass;I=np.zeros((3,3))
    for r in regions:
        d=np.asarray(r['cg_m'])-cg
        I+=np.asarray(r['inertia_kg_m2'])+r['mass_kg']*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    return dict(mass_kg=mass,cg_m=cg.tolist(),inertia_kg_m2=I.tolist())


def _uniform_region(uid,mass,centre,size,scope):
    return dict(id=uid,mass_kg=mass,cg_m=list(centre),size_m=list(size),
        inertia_kg_m2=np.diag([mass*sum(size[k]**2 for k in range(3) if k!=i)/12 for i in range(3)]).tolist(),
        distribution='uniform box assumption',scope=scope)


def validate_candidate(candidate):
    sha=candidate.get('configuration_sha256','')
    if len(sha)!=64 or any(x not in '0123456789abcdef' for x in sha):raise ValueError('exact candidate SHA required')
    if candidate.get('cars')!=6:raise ValueError('six-car candidate required')
    tare=candidate['controlled_tare_kg'];aw3=candidate['controlled_aw3_kg'];payload=candidate['passenger_payload_kg']
    if not all(_finite(x) and x>0 for x in (tare,aw3,payload)) or not math.isclose(tare+payload,aw3,abs_tol=1e-7):raise ValueError('candidate tare/AW3 ledger differs')
    p=candidate['module_placements']
    if len(p)!=24 or len({r['id'] for r in p})!=24 or any(len(r['centre_m'])!=3 or not all(_finite(x) for x in r['centre_m']) for r in p):raise ValueError('24 unique placed modules required')
    if len({tuple(r['centre_m']) for r in p})!=24:raise ValueError('overlapping duplicate attachment points')
    return candidate


def mass_properties(candidate,a=None):
    """Independent native-stock integration, never inherited20k/600k inertias.

    Module physical regions are transformed at each actual mounting point.
    Unlocated retained equipment is counted in full with disclosed placement.
    """
    a=load() if a is None else a;validate_candidate(candidate)
    stock=json.loads((DATA/'candidate-retained-body-stock.json').read_text());regions=[]
    for p in stock['parts']:
        v,c,I=primitive(p);rho=p['density_assumption_kg_m3'];c[2]-=a['placement']['retained_stock_floor_datum_m']
        regions.append(dict(id=p['id'],mass_kg=v*rho,cg_m=c.tolist(),inertia_kg_m2=(I*rho).tolist(),size_m=p['size_m'],distribution='exact signed stock primitive; assumed density'))
        regions[-1]['gravity_projection']=dict(part=p,density_kg_m3=rho)
    retained_mass=sum(r['mass_kg'] for r in regions)
    if not math.isclose(retained_mass,stock['mass_kg_per_car'],abs_tol=1e-7):raise ValueError('retained snapshot primitive mass mismatch')
    module=candidate['module'];parts=module['parts'];module_mass=0
    for placement in candidate['module_placements']:
        rotation=np.asarray(placement.get('rotation_matrix',np.eye(3)),dtype=float)
        if rotation.shape!=(3,3) or not np.allclose(rotation@rotation.T,np.eye(3),atol=1e-10):raise ValueError('orthonormal module placement axes required')
        origin=np.asarray(placement['centre_m'])
        for p in parts:
            if 'mass_kg' in p and 'cg_m' in p and 'inertia_kg_m2' in p:
                mass=p['mass_kg'];c=np.asarray(p['cg_m']);I=np.asarray(p['inertia_kg_m2'])
            else:
                v,c,I=primitive(p);rho=p['density_kg_m3'];mass=v*rho;I*=rho
            if not _finite(mass) or mass<=0 or I.shape!=(3,3):raise ValueError('physical module part mass/inertia required')
            regions.append(dict(id=placement['id']+'/'+p['id'],mass_kg=mass,cg_m=(origin+rotation@c).tolist(),inertia_kg_m2=(rotation@I@rotation.T).tolist(),distribution='placed module material region'))
            if 'size_m' in p:regions[-1]['size_m']=(np.abs(rotation)@np.asarray(p['size_m'])).tolist()
            if np.allclose(rotation,np.eye(3)):
                pp=deepcopy(p);pp['at_m']=(np.asarray(p['at_m'])+origin).tolist();pv,_,_=primitive(pp);regions[-1]['gravity_projection']=dict(part=pp,density_kg_m3=mass/pv)
            module_mass+=mass
    band_mass=0.
    for p in candidate.get('propulsion_band',{}).get('parts',[]):
        mass=p['mass_kg'];pv,_,_=primitive(p);regions.append(dict(id=p['id'],mass_kg=mass,cg_m=p['cg_m'],inertia_kg_m2=p['inertia_kg_m2'],size_m=p['size_m'],distribution='placed dedicated propulsion band material region',gravity_projection=dict(part=p,density_kg_m3=mass/pv)));band_mass+=mass
    # Supplemental equipment has explicit candidate packaging allocations and is
    # already included in the shared tare ledger: count, do not add a second time.
    protection=json.loads((DATA/'candidate-protection-equipment.json').read_text());supplement_mass=0
    for row in protection['rows']:
        if len(row['positions_m'])!=row['quantity_per_car']:raise ValueError('protection equipment count/placement mismatch')
        for i,pos in enumerate(row['positions_m']):
            regions.append(_uniform_region(row['id']+f'/{i}',row['unit_mass_kg'],pos,row['envelope_m'],'Provisional supplemental equipment envelope; not a manufactured solid'))
            supplement_mass+=row['unit_mass_kg']
    residual=candidate['controlled_tare_kg']-retained_mass-module_mass-supplement_mass-band_mass
    if residual<-1e-7:raise ValueError('defined stock exceeds controlled tare; mass ledger cannot be reconciled')
    pl=a['placement'];regions.append(_uniform_region('unlocated-retained-allocation',max(0.,residual),pl['unlocated_retained_centre_m'],pl['unlocated_retained_box_m'],'Remaining retained parent equipment/contingency, no removal credit; location is an assumption'))
    empty=_combine(regions);passenger=_uniform_region('AW3-passengers',candidate['passenger_payload_kg'],pl['passenger_centre_m'],pl['passenger_box_m'],'Uniform AW3 occupancy hypothesis, no measured load map')
    laden=_combine([*regions,passenger]);uncertainty=[]
    for z in pl['unlocated_retained_height_range_m']:
        changed=deepcopy(regions);changed[-1]['cg_m'][2]=z
        uncertainty.append(dict(residual_cg_z_m=z,**_combine([*changed,passenger])))
    return dict(empty=empty,laden=laden,known_stock_mass_kg=retained_mass,new_module_mass_kg=module_mass,
        supplemental_mass_kg=supplement_mass,propulsion_band_mass_kg=band_mass,unlocated_retained_mass_kg=residual,regions=[*regions,passenger],
        retained_placement_height_sensitivity=uncertainty,complete_installed_distribution=False,
        scope='Exact material integrals and parallel-axis composition conditional on source placements/densities; unlocated allocation and passengers are explicit uniform boxes. No measured CG/inertia or flexible-body validation.')


def _cross(r):
    x,y,z=r;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]],dtype=float)


def reactions(points,force_n,moment_nm,excluded=()):
    """Full6DOF least-norm reactions with unilateral upward support active set.

    An elastic equal-compliance allocation, not a structural stiffness solution.
    Failed modules are removed from every DOF; no artificial force clipping.
    """
    points=np.asarray(points,dtype=float);target=np.r_[force_n,moment_nm];active=[i for i in range(len(points)) if i not in excluded]
    if len(active)<3:raise ValueError('insufficient noncollinear support geometry')
    while True:
        B=np.concatenate([np.vstack((np.eye(3),_cross(points[i]))) for i in active],axis=1)
        if np.linalg.matrix_rank(B)!=6:raise ValueError('support wrench rank deficient')
        values=np.linalg.lstsq(B,target,rcond=None)[0].reshape(-1,3)
        negative=[active[j] for j,v in enumerate(values) if v[2]<-1e-7]
        if not negative:break
        active=[i for i in active if i not in negative]
        if len(active)<3:raise ValueError('no unilateral reaction solution')
    result=np.zeros_like(points)
    for i,v in zip(active,values):result[i]=v
    actual=np.r_[result.sum(axis=0),sum(np.cross(p,f) for p,f in zip(points,result))]
    error=actual-target
    if max(abs(error))>1e-5*max(1.,max(abs(target))):raise ValueError('reaction equilibrium could not be established')
    return dict(forces_n=result.tolist(),target_wrench=np.asarray(target).tolist(),recovered_wrench=actual.tolist(),equilibrium_residual=error.tolist(),
        excluded=list(excluded),inactive_tension_supports=[i for i in range(len(points)) if i not in active and i not in excluded],allocation='equal-compliance6DOF unilateral equilibrium; not dynamic load sharing')


def load_cases(candidate,mass,a=None):
    a=load() if a is None else a;l=a['loads'];m=mass['laden']['mass_kg'];cg=np.asarray(mass['laden']['cg_m']);I=np.asarray(mass['laden']['inertia_kg_m2']);g=l['gravity_m_s2'];points=[r['centre_m'] for r in candidate['module_placements']]
    lost=max(range(len(points)),key=lambda i:points[i][0]+points[i][1]);cases=[]
    inputs=[('AW3-static',[0,0,g],[0,0,0],(),0),('AW3-vertical-dynamic',[0,0,g*l['normal_dynamic_factor']],[0,0,0],(),0),
        ('emergency-braking-on-downgrade',[l['braking_deceleration_m_s2']+g*l['downgrade'],0,g],[0,0,0],(),0),
        ('asymmetric-occupancy-lateral',[0,l['lateral_acceleration_m_s2'],g*1.1],[0,0,0],(),l['passenger_lateral_offset_m']*candidate['passenger_payload_kg']/m),
        ('one-forward-outboard-support-lost',[l['braking_deceleration_m_s2'],l['lateral_acceleration_m_s2']/2,g*1.1],[0,0,0],(lost,),0),
        ('angular-response-wrench',[0,l['lateral_acceleration_m_s2']/2,g],[.05,.015,.015],(),0)]
    for name,accel,alpha,excluded,dy in inputs:
        c=cg.copy();c[1]+=dy;F=m*np.asarray(accel);M=np.cross(c,F)+I@np.asarray(alpha);r=reactions(points,F,M,excluded)
        peak=max(np.linalg.norm(f) for f in r['forces_n']);r.update(id=name,acceleration_m_s2=accel,angular_acceleration_rad_s2=alpha,cg_m=c.tolist(),
            module_force_screen_n=l['module_required_force_screen_n'],peak_module_resultant_n=float(peak),force_screen_pass=bool(peak<=l['module_required_force_screen_n']),
            modules=[dict(id=p['id'],at_m=p['centre_m'],force_n=f) for p,f in zip(candidate['module_placements'],r['forces_n'])]);cases.append(r)
    protection=json.loads((DATA/'candidate-protection-equipment.json').read_text());shoe=next(r for r in protection['rows'] if r['id']=='protection/capture-shoe');padpoints=shoe['positions_m'];rated=shoe['ratings'];capture_factor=1+rated['engagement_drop_m']/rated['maximum_compression_m']
    F=m*np.array([l['braking_deceleration_m_s2'],0,g*capture_factor]);capture=reactions(padpoints,F,np.cross(cg,F));lostpads=(0,3,4,7);adverse=reactions(padpoints,F,np.cross(cg,F),lostpads)
    capture.update(id='eight-point-capture-energy-stroke',factor=capture_factor,
        drop_m=rated['engagement_drop_m'],stroke_m=rated['maximum_compression_m'],points_m=padpoints,peak_pad_force_n=float(max(np.linalg.norm(f) for f in capture['forces_n'])),
        adverse_alternate_side_loss=adverse,contact_geometry_qualified=False,
        scope='Eight exact source equipment allocations, plus four diagonally distributed pads lost. Energy-average arrest force, not peak shock/restraint. Current pad height/contact to lowered rail is unfitted and no physical recovery acceptance is claimed.')
    ordinary=cases[1];double=reactions(points,2*np.asarray(ordinary['target_wrench'][:3]),2*np.asarray(ordinary['target_wrench'][3:]));zero=reactions(points,[0,0,0],[0,0,0])
    return dict(cases=cases,capture=capture,controls=dict(double_load_reaction_ratio=float(np.linalg.norm(double['forces_n'])/np.linalg.norm(ordinary['forces_n'])),zero_load_peak_n=float(np.max(np.abs(zero['forces_n']))),
        failed_support_load_n=float(np.linalg.norm(cases[4]['forces_n'][lost]))),
        scope='Candidate-specific inertial wrench export; scalar20kN is a retained unqualified research screen, not an attachment/actuator rating. Lateral/roll/pitch cases are imposed equilibrium conditions, not demonstrated active control.')


def _gravity_moments(regions,x,gravity):
    """Exact axial projection of signed stock, uniform disclosed allocations."""
    moments=np.zeros(len(x))
    def cylinder(d,run,at,axis,rho):
        radius=d/2
        if axis==0:
            width=run;left=at[0];length=np.clip(x-left,0,width)
            return math.pi*radius**2*rho*length*(x-left-length/2)
        centre=at[0]+radius;u=np.clip(x-centre,-radius,radius);root=np.sqrt(np.maximum(0.,radius**2-u*u))
        F0=.5*(u*root+radius**2*(np.arcsin(np.clip(u/radius,-1,1))+math.pi/2));F1=-(np.maximum(0.,radius**2-u*u))**1.5/3
        return 2*rho*run*((x-centre)*F0-F1)
    for region in regions:
        projection=region.get('gravity_projection')
        if projection:
            p=projection['part'];rho=projection['density_kg_m3'];at=np.asarray(p['at_m']);size=p['size_m']
            if p['kind']=='box':
                length=np.clip(x-at[0],0,size[0]);contribution=rho*size[1]*size[2]*length*(x-at[0]-length/2)
            else:contribution=cylinder(size[0],size[2],at,'xyz'.index(p.get('cylinder_axis','z')),rho)
            for hole in p.get('holes',[]):
                axis='xyz'.index(hole.get('axis','z'));origin=at.copy()
                for i in range(3):origin[i]+=hole.get('start_m',0.) if i==axis else hole['xyz'[i]+'_m']-hole['diameter_m']/2
                contribution-=cylinder(hole['diameter_m'],hole.get('length_m',size[axis] if p['kind']=='box' else size[2]),origin,axis,rho)
            moments-=gravity*contribution;continue
        width=region.get('size_m',[.02,0,0])[0];centre=region['cg_m'][0];left=centre-width/2;length=np.clip(x-left,0,width)
        moments-=region['mass_kg']*gravity/width*length*(x-left-length/2)
    return moments


def preferred_support_loads(candidate=None,maximum_n=None,minimum_n=0.):
    """Candidate-specific, bounded static load-sharing proposal for real control.

    A minimax linear program reduces body bending using counted distributed
    mass. Its requested forces must still pass inverse-current maps and coupled
    simulation; the proposal never directly acts on the physical plant.
    """
    from scipy.optimize import linprog
    from . import candidate_magnetics
    candidate=candidate_magnetics.definition() if candidate is None else candidate;a=load();mass=mass_properties(candidate,a);g=a['loads']['gravity_m_s2'];limit=a['loads']['module_required_force_screen_n'] if maximum_n is None else maximum_n
    limits=np.asarray([limit]*24 if _finite(limit) else limit,dtype=float)
    if limits.shape!=(24,) or not np.all(np.isfinite(limits)) or np.min(limits)<=0:raise ValueError('finite positive scalar or24module bounds required')
    minimum=np.asarray([minimum_n]*24 if _finite(minimum_n) else minimum_n,dtype=float)
    if minimum.shape!=(24,) or not np.all(np.isfinite(minimum)) or np.min(minimum)<0 or np.any(minimum>limits):raise ValueError('finite nonnegative24module lower bounds not exceeding upper bounds required')
    points=np.asarray([p['centre_m'] for p in candidate['module_placements']]);x=np.linspace(-8.5,8.5,341);G=_gravity_moments(mass['regions'],x,g);B=np.maximum(x[:,None]-points[:,0],0.)
    # Columns are24realmodule forces and the maximum absolute bending t.
    A=np.r_[np.c_[B,-np.ones(len(x))],np.c_[-B,-np.ones(len(x))]];bound=np.r_[-G,G]
    cg=np.asarray(mass['laden']['cg_m']);m=mass['laden']['mass_kg'];eq=np.c_[np.vstack((np.ones(len(points)),points[:,0],points[:,1])),np.zeros(3)];rhs=m*g*np.array([1,cg[0],cg[1]])
    result=linprog(np.r_[np.zeros(len(points)),1.],A_ub=A,b_ub=bound,A_eq=eq,b_eq=rhs,bounds=[(float(lo),float(hi)) for lo,hi in zip(minimum,limits)]+[(0,None)],method='highs')
    if not result.success:return dict(configuration_sha256=candidate['configuration_sha256'],state='infeasible',passed=False,reason=result.message,maximum_module_n=float(max(limits)),per_module_maximum_n=limits.tolist(),per_module_minimum_n=minimum.tolist(),adopted=False)
    forces=result.x[:-1];M=G+B@forces;residual=eq[:,:-1]@forces-rhs
    if max(abs(residual))>1e-5 or np.any(forces<minimum-1e-7) or np.any(forces>limits+1e-7):raise ValueError('load sharing optimiser violates independently recovered constraints')
    uniform=m*g/len(points);control=G+B@np.full(len(points),uniform)
    return dict(configuration_sha256=candidate['configuration_sha256'],state='static-request-proposal',passed=True,reference_mass_kg=m,gravity_m_s2=g,maximum_module_n=float(max(limits)),per_module_maximum_n=limits.tolist(),per_module_minimum_n=minimum.tolist(),
        preferred_loads_n=forces.tolist(),preferred_load_fractions=(forces/(m*g)).tolist(),module_ids=[p['id'] for p in candidate['module_placements']],positions_m=points.tolist(),
        peak_bending_nm=float(max(abs(M))),uniform_request_peak_bending_nm=float(max(abs(control))),equilibrium_residual=residual.tolist(),
        force_vector_sha256=sha256(encoded(dict(configuration_sha256=candidate['configuration_sha256'],ids=[p['id'] for p in candidate['module_placements']],forces_n=forces.tolist(),minimum_n=minimum.tolist(),maximum_n=limits.tolist()))).hexdigest(),
        scope='Static upward request weights only. Exact actual Rust allocation, force/slew limits, current inversion, disturbances and flexible-body stability require executed confirmation; no force applied directly.',adopted=False,physical_accepted=False)


def bolt_group(force_n,moment_nm,xs,zs,prying=1.5):
    """Signed normal force + in-plane shear of a bolt group on the x-z plane."""
    pts=[(x,z) for x in xs for z in zs];n=len(pts);sx=sum(x*x for x,z in pts);sz=sum(z*z for x,z in pts);polar=sx+sz
    if min(sx,sz)<=0:raise ValueError('nondegenerate bolt group required')
    Fx,Fy,Fz=force_n;Mx,My,Mz=moment_nm;rows=[]
    for x,z in pts:
        # r×(0,N,0)=(-zN,0,xN), r×(Sx,0,Sz)=(0,zSx-xSz,0)
        N=Fy/n-Mx*z/sz+Mz*x/sx;Sx=Fx/n+My*z/polar;Sz=Fz/n-My*x/polar
        rows.append(dict(x_m=x,z_m=z,signed_normal_n=N,tension_with_prying_n=max(0,N)*prying,shear_x_n=Sx,shear_z_n=Sz,shear_n=math.hypot(Sx,Sz)))
    recovered=[sum(r['shear_x_n'] for r in rows),sum(r['signed_normal_n'] for r in rows),sum(r['shear_z_n'] for r in rows),
        sum(-r['z_m']*r['signed_normal_n'] for r in rows),sum(r['z_m']*r['shear_x_n']-r['x_m']*r['shear_z_n'] for r in rows),sum(r['x_m']*r['signed_normal_n'] for r in rows)]
    return dict(bolts=rows,recovered_wrench=recovered,equilibrium_residual=(np.asarray(recovered)-np.r_[force_n,moment_nm]).tolist(),
        maximum_tension_n=max(r['tension_with_prying_n'] for r in rows),maximum_shear_n=max(r['shear_n'] for r in rows),
        scope='Compression-side signed normal resultant includes contact bearing; prying is a declared amplification, not a plate/contact solution.')


def hardpoint_geometry(a=None):
    a=load() if a is None else a;stock=json.loads((DATA/'candidate-retained-body-stock.json').read_text())['parts']
    parts=[p for p in stock if p['id'].endswith('/carrier-flange')]
    if len(parts)!=24:raise ValueError('24 actual retained hardpoint flanges required')
    groups=[]
    for p in parts:
        at=p['at_m'];size=p['size_m'];holes=p.get('holes',[])
        if len(holes)!=16:raise ValueError('exact16-bolt flange required')
        xs=[h['x_m']-size[0]/2 for h in holes];zs=[h['z_m']-size[2]/2 for h in holes]
        if not np.allclose(sorted(set(round(x,10) for x in xs)),a['joints']['hardpoint_bolt_x_m']) or not np.allclose(sorted(set(round(z,10) for z in zs)),a['joints']['hardpoint_bolt_z_m']):raise ValueError('flange hole pattern differs from structural drawing')
        side=1 if at[1]>0 else -1;face=at[1]+size[1] if side>0 else at[1]
        groups.append(dict(id=p['id'],centre_m=[at[0]+size[0]/2,face,at[2]+size[2]/2-a['placement']['retained_stock_floor_datum_m']],size_m=size))
    return groups


def _bounds(part):
    size=np.asarray(part['size_m'],dtype=float)
    if part['kind']=='cylinder':
        axis='xyz'.index(part.get('cylinder_axis','z'));diameter=size[0];run=size[2];size=np.full(3,diameter);size[axis]=run
    at=np.asarray(part['at_m'],dtype=float)
    return at,at+size


def _inside(point,part):
    lo,hi=_bounds(part);p=np.asarray(point)
    if np.any(p<lo-1e-10) or np.any(p>hi+1e-10):return False
    if part['kind']=='cylinder':
        axis='xyz'.index(part.get('cylinder_axis','z'));indices=[i for i in range(3) if i!=axis];centre=(lo+hi)/2
        if sum((p[i]-centre[i])**2 for i in indices)>(part['size_m'][0]/2)**2:return False
    for hole in part.get('holes',[]):
        axis='xyz'.index(hole.get('axis','z'));start=lo[axis]+hole.get('start_m',0.);end=start+hole.get('length_m',hi[axis]-lo[axis]);indices=[i for i in range(3) if i!=axis]
        if start-1e-10<=p[axis]<=end+1e-10 and sum((p[i]-lo[i]-hole['xyz'[i]+'_m'])**2 for i in indices)<(hole['diameter_m']/2)**2:return False
    return True


def collision_witness(first,second):
    """Actual positive-volume overlap witness, accounting for drilled voids."""
    alo,ahi=_bounds(first);blo,bhi=_bounds(second);lo=np.maximum(alo,blo);hi=np.minimum(ahi,bhi)
    if np.any(hi-lo<=1e-9):return None
    # Not a full Boolean solver: any reported witness is actually in both
    # materials. An unreported AABB overlap remains an unresolved near-contact.
    for fx in (.5,.1,.9,.3,.7):
        for fy,fz in ((.5,.5),(.1,.1),(.9,.9),(.1,.9),(.9,.1)):
            point=lo+(hi-lo)*np.array([fx,fy,fz])
            if _inside(point,first) and _inside(point,second):return dict(point_m=point.tolist(),overlap_bounds_m=[lo.tolist(),hi.tolist()])
    return None


def interface_clearance(candidate,guideway,a=None):
    """Continuous rail vs moving vehicle/attachments, plus module-stock fit.

    This does not exempt conflicting historic parts. Named joint contacts are
    only exact common faces; equivalent fastener envelopes are excluded from
    solid interference assertions and stay an explicit fit hold.
    """
    a=load() if a is None else a;retained=deepcopy(json.loads((DATA/'candidate-retained-body-stock.json').read_text())['parts'])
    for p in retained:p['at_m'][2]-=a['placement']['retained_stock_floor_datum_m']
    attachment=json.loads((DATA/'candidate-attachment-equipment.json').read_text());byid={p['id']:p for p in retained};operations=[]
    if any(p['id'].startswith('top-plate/') for p in candidate['module']['parts']):
        for op in attachment.get('retained_machining',[]):
            part=byid[op['target_part_id']];lo,hi=_bounds(part)
            for x,y in op['world_centres_xy_m']:
                part.setdefault('holes',[]).append(dict(axis='z',diameter_m=op['diameter_m'],x_m=x-lo[0],y_m=y-lo[1],start_m=0.,length_m=hi[2]-lo[2]))
            operations.append(op)
    added=[]
    for placement in candidate['module_placements']:
        if not np.allclose(placement.get('rotation_matrix',np.eye(3)),np.eye(3)):raise ValueError('clearance checker requires explicit axis-aligned placement')
        for p in candidate['module']['parts']:
            if p.get('equivalent_box'):continue
            q=deepcopy(p);q['id']=placement['id']+'/'+p['id'];q['at_m']=(np.asarray(p['at_m'])+placement['centre_m']).tolist();added.append(q)
    # Dedicated propulsion arrays are vehicle parts too, not fixed wayside rail.
    added.extend(deepcopy(candidate.get('propulsion_band',{}).get('parts',[])))
    fixed=guideway['parts'];findings=[];counts=dict(rail_retained=0,rail_added=0,added_retained=0,module_internal=0);near_count=0
    def check(first,second,kind):
        nonlocal near_count
        witness=collision_witness(first,second)
        if witness:
            counts[kind]+=1
            if len(findings)<160:findings.append(dict(kind=kind,first=first['id'],second=second['id'],**witness))
        else:
            lo,hi=_bounds(first);lo2,hi2=_bounds(second)
            if np.all(np.minimum(hi,hi2)-np.maximum(lo,lo2)>0):near_count+=1
    # Vectorised broad-phase avoids O(material regions²) scalar checking.
    def compare(left,right,kind):
        bounds=[_bounds(p) for p in right];los=np.asarray([x[0] for x in bounds]);his=np.asarray([x[1] for x in bounds])
        for p in left:
            lo,hi=_bounds(p);matches=np.where(np.all(np.minimum(hi,his)-np.maximum(lo,los)>1e-9,axis=1))[0]
            for i in matches:check(p,right[int(i)],kind)
    compare(fixed,retained,'rail_retained');compare(fixed,added,'rail_added');compare(added,retained,'added_retained')
    module_parts=[p for p in candidate['module']['parts'] if not p.get('equivalent_box')]
    for i,p in enumerate(module_parts):
        for q in module_parts[i+1:]:check(p,q,'module_internal')
    return dict(counts=counts,material_interference_count=sum(counts.values()),findings=findings,retained_machining_operations_applied=operations,unresolved_overlapping_bounds_without_sample_witness=near_count,
        passed_no_material_witness=sum(counts.values())==0,clearance_tolerance_approved=False,
        scope='Box/cylinder point-in-material witnesses account for drilled voids; a material witness is a definite interference. Absence is bounded AABB/point screening, not continuous swept native collision/tolerance acceptance. Rails extend continuously across25m, so their static overlap also obstructs through motion.')


def mechanical(candidate,mass,loads,a=None):
    a=load() if a is None else a;j=a['joints'];s=a['steel'];governing=[];geometry=hardpoint_geometry(a)
    for case in loads['cases']:
        for module in case['modules']:
            F=np.asarray(module['force_n']);side=1 if module['at_m'][1]>0 else -1
            flange=min(geometry,key=lambda p:np.linalg.norm(np.asarray(p['centre_m'])[:2]-np.asarray(module['at_m'])[:2]));r=np.asarray(module['at_m'])-np.asarray(flange['centre_m']);moment=np.cross(r,F)
            # Mirror y-side load path in actual vehicle coordinates. Plate group
            # is equally symmetric; no force is derived from the old26.4t screen.
            localF=F*np.array([1,side,1]);localM=moment*np.array([side,1,side])
            group=bolt_group(localF,localM,j['hardpoint_bolt_x_m'],j['hardpoint_bolt_z_m'],j['prying_factor'])
            tension=group['maximum_tension_n'];shear=group['maximum_shear_n'];pullthrough=math.pi*j['washer_outside_diameter_m']*j['steel_stringer_wall_m']*s['shear_screen_pa']
            boltT=j['hardpoint_bolt_thread_area_m2']*s['bolt_tension_screen_pa'];boltV=j['hardpoint_bolt_thread_area_m2']*s['bolt_shear_screen_pa']
            strip=(j['carrier_plate_width_m']-max(j['hardpoint_bolt_x_m'])*2)/2
            flange_stress=6*tension*strip/(.050*j['carrier_flange_thickness_m']**2)
            upright_net=(j['upright_width_m']-2*j['upright_service_hole_m'])*j['upright_thickness_m']
            upright_stress=(abs(F[2])+abs(moment[0])/.170)/upright_net
            governing.append(dict(case=case['id'],module=module['id'],force_n=F.tolist(),joint_centre_m=flange['centre_m'],load_arm_m=r.tolist(),joint_moment_nm=moment.tolist(),bolt_group=group,
                local_bolt_force_n=localF.tolist(),local_bolt_moment_nm=localM.tolist(),bolt_group_normal_convention='local+y is outboard tensile on each vehicle side; moments transformed as axial vectors',
                bolt_tension_n=tension,bolt_shear_n=shear,pull_through_screen_n=pullthrough,flange_stress_pa=flange_stress,upright_net_stress_pa=upright_stress,
                utilisation=max(tension/boltT,shear/boltV,tension/pullthrough,flange_stress/s['aluminium_stress_screen_pa'],upright_stress/s['stress_screen_pa']),
                preload_wall_crush_qualified=False,fastener_fatigue_qualified=False))
    worst=max(governing,key=lambda r:r['utilisation']);Fmax=max(m['force_n'][2] for c in loads['cases'] for m in c['modules'])
    b,h=j['collector_outside_m'];t=j['collector_wall_m'];I=(b*h**3-(b-2*t)*(h-2*t)**3)/12;Z=I/(h/2)
    moment=Fmax*j['splice_transfer_arm_m']*j['splice_transfer_fraction'];plate=j['splice_old_plate_m'];boltAs=j['splice_old_bolt_thread_area_m2'];n=j['splice_old_bolts_per_cut']
    group=bolt_group([0,0,Fmax],[moment,0,0],[-.075,-.025,.025,.075],[-j['splice_old_vertical_row_pitch_m']/2,j['splice_old_vertical_row_pitch_m']/2],j['prying_factor'])
    old_splice=dict(id='retained-M8-segment-splice',per_cut_bolts=n,cut_count_per_car=48,plate_per_cut=2,force_n=Fmax,transfer_arm_m=j['splice_transfer_arm_m'],moment_nm=moment,
        maximum_bolt_tension_n=group['maximum_tension_n'],maximum_bolt_shear_n=group['maximum_shear_n'],collector_stress_pa=moment/Z,
        utilisation=max(group['maximum_tension_n']/(boltAs*s['bolt_tension_screen_pa']),group['maximum_shear_n']/(boltAs*s['bolt_shear_screen_pa']),moment/Z/s['stress_screen_pa']),
        collector_I_m4=I,plate_m=plate,load_path='Accidental full module load crosses one cut at0.5m arm. Ordinary direct hardpoint transfer is not credited during this continuity case.',
        passed=False,scope='Failure cannot be cured by assuming the removed cartridge carries bending; detailed joint/contact/fatigue remains open.')
    old_splice['passed']=old_splice['utilisation']<=1
    # Real alternative geometry/stock: count changes but do not silently add
    # them to the shared candidate mass and claim the old physics still applies.
    altb,alth,altt=.12,.16,.010;altI=(altb*alth**3-(altb-2*altt)*(alth-2*altt)**3)/12
    altZ=altI/(alth/2);altgroup=bolt_group([0,0,Fmax],[moment,0,0],[-.075,-.025,.025,.075],[-.10,.10],j['prying_factor']);As16=157e-6
    added_collector=(altb*alth-(altb-2*altt)*(alth-2*altt)-(b*h-(b-2*t)*(h-2*t)))*24*s['density_kg_m3']
    plate_mass=48*2*.22*.28*.020*s['density_kg_m3'];oldplate_mass=48*2*math.prod(plate)*s['density_kg_m3']
    upgrade=dict(id='deeper-collector-flanged-M16-splice',collector_outside_m=[altb,alth],wall_m=altt,flange_m=[.22,.020,.28],bolts_per_cut=8,bolt_diameter_m=.016,
        bolt_group=altgroup,collector_stress_pa=moment/altZ,additional_stock_mass_kg_per_car=added_collector+max(0.,plate_mass-oldplate_mass),
        utilisation=max(moment/altZ/s['stress_screen_pa'],altgroup['maximum_tension_n']/(As16*s['bolt_tension_screen_pa']),altgroup['maximum_shear_n']/(As16*s['bolt_shear_screen_pa'])),
        requires_candidate_revision=True,packaging_and_service_path_fitted=False,scope='Unselected continuity alternative; counts added collector/plates conservatively, bolts/fabrication and actual bore/edge/handling fit remain open. Requires re-closed mass and repeated dynamics.')
    # Net drilled steel tube bending/axial section from the controlled stock.
    bw,hh,wall=.14,.22,.004;area=bw*hh-(bw-2*wall)*(hh-2*wall);inertia=(bw*hh**3-(bw-2*wall)*(hh-2*wall)**3)/12
    # Two13mm cross-wall bores on each stringer at an attachment section.
    netarea=area-4*j['bolt_hole_diameter_m']*wall;netI=inertia-4*j['bolt_hole_diameter_m']*wall*.085**2
    # Equilibrated applied gravity and support reactions along the actual car.
    x=np.linspace(-8.5,8.5,681);curve=_gravity_moments(mass['regions'],x,a['loads']['gravity_m_s2']*a['loads']['normal_dynamic_factor']);case=loads['cases'][1]
    for module in case['modules']:curve+=np.maximum(0.,x-module['at_m'][0])*module['force_n'][2]
    maxM=max(abs(v) for v in curve);brake=mass['laden']['mass_kg']*(a['loads']['braking_deceleration_m_s2']+a['loads']['gravity_m_s2']*a['loads']['downgrade'])
    axial=brake/(2*netarea);bend=maxM*hh/2/(2*netI)
    fatigue=[dict(stress_range_pa=2*bend,reference_range_pa=limit,cycles=a['steel']['fatigue_cycles'],damage=a['steel']['fatigue_cycles']/a['steel']['fatigue_reference_cycles']*(2*bend/limit)**a['steel']['fatigue_slope'],detail_category_qualified=False) for limit in s['fatigue_range_screens_pa']]
    spine=dict(material='steel',outside_m=[bw,hh],wall_m=wall,count=2,net_area_each_m2=netarea,net_I_each_m4=netI,bending_moment_peak_nm=maxM,
        braking_axial_n=brake,axial_stress_pa=axial,bending_stress_pa=bend,combined_screen_pa=axial+bend,stress_limit_pa=s['stress_screen_pa'],
        passed=axial+bend<=s['stress_screen_pa'],fatigue=fatigue,shear_bond_and_local_buckling_qualified=False,
        end_moment_residual_nm=curve[-1],moment_samples=[dict(x_m=float(xx),moment_nm=float(mm)) for xx,mm in zip(x[::20],curve[::20])],
        scope='Independent1D equilibrium of distributed counted masses and point supports; cabin skin/frame composite stiffness omitted. Net section includes actual13mm bores; variable stiffness/doors/bonds/flexible-body dynamics remain unqualified.')
    alternative_spines=[]
    for width,depth,thickness in ((.14,.28,.006),(.18,.32,.006),(.18,.36,.006)):
        A=width*depth-(width-2*thickness)*(depth-2*thickness);Ic=(width*depth**3-(width-2*thickness)*(depth-2*thickness)**3)/12
        top=-.2055;centre=top-depth/2;holelevels=[-.3155-.085,-.3155+.085];An=A-4*j['bolt_hole_diameter_m']*thickness
        In=Ic-sum(2*thickness*(j['bolt_hole_diameter_m']**3/12+j['bolt_hole_diameter_m']*(z-centre)**2) for z in holelevels)
        stress=brake/(2*An)+maxM*depth/2/(2*In);stock_increment=2*17*(A-area)*s['density_kg_m3']
        #384actual through-bolts/spacers retain the sameouter attachment face;
        # a wider inward tube requires longer grips, never hidden shortening.
        grip=max(0.,width-bw);spacer_increment=384*math.pi*(.025**2-.013**2)/4*grip*s['density_kg_m3'];bolt_increment=384*math.pi*.012**2/4*grip*s['density_kg_m3']
        alternative_spines.append(dict(id=f'steel-spine-{width:g}-{depth:g}-{thickness:g}',outside_m=[width,depth],wall_m=thickness,top_z_m=top,
            net_area_each_m2=An,net_I_each_m4=In,stress_pa=stress,stress_limit_pa=s['stress_screen_pa'],passed_fixed_load_screen=stress<=s['stress_screen_pa'],
            added_tube_stock_kg=stock_increment,added_grip_spacer_kg=spacer_increment,added_bolt_shank_kg=bolt_increment,
            additional_mass_kg_per_car=stock_increment+spacer_increment+bolt_increment,additional_fabricated_stock_cost_usd=(stock_increment+spacer_increment+bolt_increment)*a['rates']['fabricated_structural_steel_usd_kg'],
            requires_candidate_revision=True,changed_AW3_not_simulated=True,full_bolt_plate_fit_qualified=False,
            scope='Two actual deeper steel tubes extend inward/below, preservingouterface/topdatum and16M12holelevels. Fixed-load screen is not mass-recursive adoption; newmass/inertia/phaseEA/dynamics and nativefit must close together.'))
    axial_EA=2*netarea*s['young_pa'];body_k=axial_EA/a['loads']['car_length_m'];coupler_k=s['coupler_stiffness_assumption_n_m']
    spine.update(axial_EA_n=axial_EA,body_axial_stiffness_n_m=body_k,coupler_stiffness_assumption_n_m=coupler_k,
        body_and_coupler_series_stiffness_n_m=1/(1/body_k+1/coupler_k),coupler_stiffness_measured=False,alternatives=alternative_spines)
    capture=loads['capture'];energy=.5*mass['laden']['mass_kg']*25**2
    brake_screen=dict(speed_assumption_m_s=25,kinetic_energy_j_per_car=energy,grade_power_w_at_speed=mass['laden']['mass_kg']*a['loads']['gravity_m_s2']*a['loads']['downgrade']*25,
        required_longitudinal_n=brake,wet_friction_assumption=.15,required_total_normal_n=brake/.15,capture_peak_average_pad_n=capture['peak_pad_force_n'],
        capture_heat_and_force_displacement_qualified=False,beam_local_contact_qualified=False)
    return dict(hardpoint=dict(worst=worst,passed=worst['utilisation']<=1,load_cases_checked=len(governing),all_load_cases=governing),collector_splice=old_splice,
        alternatives=[upgrade],body_spine=spine,brake_capture=brake_screen,
        scope='Recomputed exact-candidate demands; neither historical26.4t joint result nor successful94ad actuator dynamics is structural acceptance.')


def axial_properties(candidate=None):
    """Net drilled steel axial EA; coupler spring is a disclosed hypothesis."""
    from . import candidate_magnetics
    candidate=candidate_magnetics.definition() if candidate is None else candidate;a=load();b,h,t=.14,.22,.004;A=b*h-(b-2*t)*(h-2*t)-4*.013*t;EA=2*A*a['steel']['young_pa'];length=a['loads']['car_length_m'];K=EA/length;kc=a['steel']['coupler_stiffness_assumption_n_m']
    return dict(configuration_sha256=candidate['configuration_sha256'],axial_EA_n=EA,body_length_m=length,body_axial_stiffness_n_m=K,coupler_stiffness_assumption_n_m=kc,
        body_and_coupler_series_stiffness_n_m=1/(1/K+1/kc),coupler_measured=False,
        scope='Two actual steel4mm drilled stringers, no cabin composite credit.100MN/m coupler is a retained hypothetical spring, not a qualified coupler drawing/rating.',qualified=False)


def vehicle_handling(candidate,mass,a=None):
    """Counted ten-fork external lifting frame, separate from installed mass."""
    a=load() if a is None else a;g=a['loads']['gravity_m_s2'];rho=a['steel']['density_kg_m3'];empty=mass['empty'];cg=np.asarray(empty['cg_m']);factor=1.3
    # Intermediate forks use integerx gaps between carrieruprights at halfx.
    # Side hangers stay outside the1.48m retained carrier envelope; fork pads
    # touch the steel stringer underside, not an unqualified cabin roof skin.
    xs=[-7.5,-3.,0.,3.,7.5];points=[[x,y,-.4255] for x in xs for y in (-1.1,1.1)]
    F=np.array([0,0,empty['mass_kg']*g*factor]);r=reactions(points,F,np.cross(cg,F));xgrid=np.linspace(-8.5,8.5,341);regions=[p for p in mass['regions'] if p['id']!='AW3-passengers'];G=_gravity_moments(regions,xgrid,g*factor);pts=np.asarray(points);B=np.maximum(xgrid[:,None]-pts[:,0],0.)
    from scipy.optimize import linprog
    equalities=np.c_[np.vstack((np.ones(len(pts)),pts[:,0],pts[:,1])),np.zeros(3)];rhs=empty['mass_kg']*g*factor*np.array([1,cg[0],cg[1]])
    opt=linprog(np.r_[np.zeros(len(pts)),1.],A_ub=np.r_[np.c_[B,-np.ones(len(xgrid))],np.c_[-B,-np.ones(len(xgrid))]],b_ub=np.r_[-G,G],A_eq=equalities,b_eq=rhs,bounds=[(0,100000)]*len(pts)+[(0,None)],method='highs')
    if not opt.success:raise ValueError('proposed ten-fork handling fixture cannot recover bounded static equilibrium')
    forces=np.c_[np.zeros((len(pts),2)),opt.x[:-1]];M=G+B@opt.x[:-1]
    if max(abs(equalities[:,:-1]@opt.x[:-1]-rhs))>1e-5:raise ValueError('handling fixture reaction residual differs')
    # Distinct end-only handling control is retained; it must not be confused
    # with the actual operating24hanger load case or chosen multi-pick fixture.
    endpoints=[[-8.,-1.1,-.4255],[-8.,1.1,-.4255],[8.,-1.1,-.4255],[8.,1.1,-.4255]];end=reactions(endpoints,F,np.cross(cg,F));Me=_gravity_moments(regions,xgrid,g*factor)
    for point,force in zip(endpoints,end['forces_n']):Me+=np.maximum(xgrid-point[0],0)*force[2]
    def area(b,h,t):return b*h-(b-2*t)*(h-2*t)
    chordA=area(.12,.12,.008);diagA=area(.06,.06,.004);yokeA=area(.12,.16,.010)
    bars=[dict(id='fixture/truss-chords',quantity=4,length_each_m=17.,outside_m=[.12,.12],wall_m=.008,mass_kg=4*17*chordA*rho),
        dict(id='fixture/truss-diagonals',quantity=12,length_each_m=math.hypot(17/6,1),outside_m=[.06,.06],wall_m=.004,mass_kg=12*math.hypot(17/6,1)*diagA*rho),
        dict(id='fixture/truss-verticals',quantity=14,length_each_m=1.,outside_m=[.06,.06],wall_m=.004,mass_kg=14*diagA*rho),
        dict(id='fixture/side-hangers',quantity=10,length_each_m=4.55,outside_m=[.12,.12],wall_m=.008,mass_kg=10*4.55*chordA*rho),
        dict(id='fixture/under-spine-forks',quantity=10,length_each_m=.55,outside_m=[.12,.16],wall_m=.010,mass_kg=10*.55*yokeA*rho),
        dict(id='fixture/top-crossheads',quantity=5,length_each_m=3.2,outside_m=[.12,.16],wall_m=.010,mass_kg=5*3.2*yokeA*rho),
        dict(id='fixture/pads',quantity=10,size_m=[.30,.14,.02],mass_kg=10*.30*.14*.02*rho),
        dict(id='fixture/rigging-and-master-lugs',quantity=1,mass_kg=500.,basis='Counted planning allowance; lug/chain/reeving ratings unqualified'),
        dict(id='fixture/equalizing-links-and-loadcells',quantity=10,mass_kg=150.,basis='15kg per monitored adjustable pick allocation; equalisation mechanism, ratings and vendor quotation remain held')]
    fixturemass=sum(p['mass_kg'] for p in bars);moment=empty['mass_kg']*g*factor*17/8;chordforce=moment/1.;stress=chordforce/chordA
    netI=(.14*.22**3-.132*.212**3)/12-4*.013*.004*.085**2;body_stress=max(abs(M))*.11/(2*netI)
    return dict(configuration_sha256=candidate['configuration_sha256'],fixture_installed_on_train=False,fixture_bom=bars,fixture_mass_kg=fixturemass,
        vehicle_tare_kg=empty['mass_kg'],suspended_vehicle_and_fixture_kg=empty['mass_kg']+fixturemass,pick_points_m=points,pick_reactions_n=forces.tolist(),pick_force_limit_assumption_n=100000,
        equilibrium_residual=(equalities[:,:-1]@opt.x[:-1]-rhs).tolist(),equalizing_and_loadcell_plan_qualified=False,
        body_lifting_moment_nm=float(max(abs(M))),body_lifting_spine_stress_pa=float(body_stress),body_lifting_screen_pass=bool(body_stress<=a['steel']['stress_screen_pa']),
        truss_chord_force_n=chordforce,truss_chord_stress_pa=stress,truss_static_screen_pass=stress<=a['steel']['stress_screen_pa'],
        end_only_rejected_control=dict(pick_points_m=endpoints,maximum_moment_nm=float(max(abs(Me))),spine_stress_pa=float(max(abs(Me))*.11/(2*netI))),
        side_hanger_centres_y_m=[-1.60,1.60],fork_x_positions_m=xs,upper_truss_z_m=[4.,5.],
        purchase_stock_cost_planning_usd=fixturemass*a['rates']['fabricated_structural_steel_usd_kg'],mass_added_to_vehicle_kg=0.,
        accepted=False,scope='External ten-fork fixture geometry avoids using cabin roof skins as lifting points. Static truss/vehicle spine screens only; native fit, lugs/welds/pad crushing/temporary bracing, unequal sling sharing, sway and competent lifting-plan acceptance remain open.')


def protection_structures(candidate,mass,loads,a=None):
    a=load() if a is None else a;data=json.loads((DATA/'candidate-protection-equipment.json').read_text());shoe=next(r for r in data['rows'] if r['id']=='protection/capture-shoe');brake=next(r for r in data['rows'] if r['id']=='protection/independent-guideway-brake');m=mass['laden']['mass_kg'];g=a['loads']['gravity_m_s2'];sr=shoe['ratings'];br=brake['ratings']
    drop=sr['engagement_drop_m'];stroke=sr['maximum_compression_m'];needed=m*g*(1+drop/stroke);available=shoe['quantity_per_car']*sr['maximum_normal_force_n']
    clamp=br['clamp_normal_n'];force=brake['quantity_per_car']*clamp*br['friction_coefficient'];grade=m*g*a['loads']['downgrade'];net=force-grade;v=25.;deceleration=net/m;distance=v*v/(2*deceleration) if net>0 else None
    energy=.5*m*v*v;work=energy*force/net if net>0 else None;thermalmass=brake['quantity_per_car']*br['thermal_effective_mass_kg'];temperature=40+work*br['vehicle_heat_fraction']/(thermalmass*br['thermal_specific_heat_j_kg_k']) if work is not None else None
    tie=next(r for r in data['rows'] if r['id']=='protection/brake-cross-tie');stock=tie['stock'][0];outer=stock['outer_m'];inner=stock['inner_m'];A=outer[0]*outer[2]-inner[0]*inner[2];stress=clamp/A
    # Actual inner L-web plane supports capture over its web centre, avoiding
    # the long top-flange outstand. Brake normal force still bends the web
    # locally between its bearing seat and pad centre.
    webt=.025;webheight=.233;padlength=brake['envelope_m'][0];M=clamp*webheight/2;webstress=6*M/(padlength*webt**2)
    return dict(configuration_sha256=candidate['configuration_sha256'],capture=dict(count=shoe['quantity_per_car'],positions_m=shoe['positions_m'],ratings=sr,
        total_force_ceiling_n=available,unsupported_energy_average_required_n=needed,unsupported_drop_screen_pass=needed<=available,
        residual_magnetic_support_not_credited_n=0.,source_capture_loads=loads['capture'],
        scope='Whole-car passive loss-of-lift energy control. Reserve-supported partial failures must be evaluated separately; a50k clip is not proof that the vehicle stops within8mm.'),
        braking=dict(count=brake['quantity_per_car'],positions_m=brake['positions_m'],normal_each_n=clamp,friction_coefficient=br['friction_coefficient'],total_available_n=force,
            downgrade_resistance_n=grade,net_deceleration_m_s2=deceleration,initial_speed_m_s=v,stopping_distance_m=distance,braking_work_including_downgrade_j=work,
            effective_onboard_heat_capacity_j_k=thermalmass*br['thermal_specific_heat_j_kg_k'],temperature_estimate_c=temperature,temperature_screen_c=br['temperature_screen_c'],
            required_deceleration_m_s2=a['loads']['braking_deceleration_m_s2'],deceleration_screen_pass=deceleration>=a['loads']['braking_deceleration_m_s2'],thermal_screen_pass=temperature is not None and temperature<=br['temperature_screen_c'],
            no_wayside_cooling_credit=True),
        cross_tie=dict(count=tie['quantity_per_car'],outside_m=outer,inside_m=inner,area_m2=A,axial_n=clamp,stress_pa=stress,stress_screen_pa=a['steel']['stress_screen_pa'],passed=stress<=a['steel']['stress_screen_pa'],joints_and_buckling_qualified=False),
        inner_return_web=dict(thickness_m=webt,loaded_height_m=webheight,normal_each_n=clamp,local_bending_moment_nm=M,stress_screen_pa=webstress,passed=webstress<=a['steel']['stress_screen_pa'],
            lamination_stack_clamp_and_fastener_transfer_qualified=False),
        accepted=False,scope='Exact new shoe/brake/tie allocations and source-rated assumptions. Passive full-drop, downhill stopping/heat, local web and tie are independent screens; actual contacts, local FE, lamination shear/clamps, mounts and physical tests remain open.')


def section_properties(section):
    b=section['width_m'];h=section['depth_m'];tw=section['web_m'];tf=section['flange_m']
    if not (b>2*tw>0 and h>2*tf>0):raise ValueError('positive hollow box section required')
    area=b*h-(b-2*tw)*(h-2*tf);I=(b*h**3-(b-2*tw)*(h-2*tf)**3)/12
    Iy=(h*b**3-(h-2*tf)*(b-2*tw)**3)/12;Ak=(b-tw)*(h-tf)
    J=4*Ak*Ak/(2*(b-tw)/tf+2*(h-tf)/tw)
    return dict(area_m2=area,I_m4=I,weak_I_m4=Iy,Z_m3=I/(h/2),torsion_midline_area_m2=Ak,torsion_J_m4=J)


def return_rail_and_attachments(candidate,span_m=25.,a=None):
    """New L-return steel plus real transverse supports; no old steel allowance."""
    from . import candidate_magnetics
    a=load() if a is None else a;r=a['rail_support'];rho=a['steel']['density_kg_m3']
    guideway=candidate_magnetics.guideway_definition(span_m,variant_id=candidate['variant_id'])
    if guideway['configuration_sha256']!=candidate['configuration_sha256']:raise ValueError('return rail and vehicle candidate identity differ; source changed or candidate is stale')
    rows=guideway['parts'];rail_volume=math.fsum(p['volume_m3'] for p in rows)
    rail_mass=math.fsum(p['mass_kg'] for p in rows)
    if len({p['id'] for p in rows})!=len(rows) or any(p['volume_m3']<=0 or p['mass_kg']<=0 for p in rows):raise ValueError('unique physical L-return rail regions required')
    count=math.ceil(span_m/r['crossmember_pitch_m'])+1;actual_pitch=span_m/(count-1)
    b=r['crossmember_width_m'];h=r['crossmember_depth_m'];t=r['crossmember_wall_m'];area=b*h-(b-2*t)*(h-2*t)
    I=(b*h**3-(b-2*t)*(h-2*t)**3)/12;crossmass=count*area*r['crossmember_length_m']*rho
    platemass=count*r['baseplates_per_crossmember']*math.prod(r['baseplate_m'])*rho
    # Slender-in-y risers occupy the actual slots outside both module edges.
    # Inner risers move inboard of the dedicated propulsion band, with counted
    # short top offsets to the rail webs. All coordinates are finished-floor.
    support_parts=[]
    def box(uid,size,at):
        v,c,I=_box(size,at);support_parts.append(dict(id=uid,kind='box',size_m=size,at_m=at,volume_m3=v,mass_kg=v*rho,cg_m=c.tolist(),inertia_kg_m2=(I*rho).tolist(),material='structural-steel-hypothesis'))
    def tube(uid,axis,length,breadth,depth,wall,at):
        u,v=[i for i in range(3) if i!=axis]
        for side in (0,1):
            size=[0.,0.,0.];size[axis]=length;size[u]=wall;size[v]=depth;pos=list(at);pos[u]+=side*(breadth-wall);box(uid+f'/wall-u-{side}',size,pos)
        for side in (0,1):
            size=[0.,0.,0.];size[axis]=length;size[u]=breadth-2*wall;size[v]=wall;pos=list(at);pos[u]+=wall;pos[v]+=side*(depth-wall);box(uid+f'/wall-v-{side}',size,pos)
    riser_mass=0.;riser_lengths=[];top=r['crossmember_top_z_m'];postx=r['rail_riser_longitudinal_m'];posty=r['rail_riser_transverse_m'];postwall=r['rail_riser_wall_m']
    for i in range(count):
        x=-span_m/2+i*actual_pitch
        tube(f'fixed-support/{i}/crossmember',1,r['crossmember_length_m'],b,h,t,[x-b/2,-r['crossmember_length_m']/2,top-h])
        for face in guideway['faces']:
            rail_y,_=face['attachment_line_m'];web=next(p for p in guideway['parts'] if p['id']==face['id']+'/web');z=web['at_m'][2]-.012
            side=1 if rail_y>0 else -1;postcentre=side*r['inner_riser_centre_y_m'] if abs(rail_y)<.88 else rail_y
            length=z-top
            if length<=0:raise ValueError('fixed riser must reach actual return attachment above crossmember')
            before=len(support_parts);tube(f'fixed-support/{i}/'+face['id']+'/riser',2,length,postx,posty,postwall,[x-postx/2,postcentre-posty/2,top]);riser_mass+=sum(p['mass_kg'] for p in support_parts[before:]);riser_lengths.append(length)
            # Actual short bearing cap connects inboard riser to the web; this
            # joint is steel-to-steel, not an unsupported line in a drawing.
            width=abs(rail_y-postcentre)+posty
            box(f'fixed-support/{i}/'+face['id']+'/cap',[postx,width,.012],[x-postx/2,min(postcentre,rail_y)-posty/2,z])
        for side in (-1,1):
            sz=r['baseplate_m'];box(f'fixed-support/{i}/baseplate-{side}',sz,[x-sz[0]/2,side*.35-sz[1]/2,top-h-sz[2]])
    all_support_mass=sum(p['mass_kg'] for p in support_parts);capsmass=all_support_mass-crossmass-platemass-riser_mass
    return dict(guideway=guideway,rail_mass_kg=rail_mass,rail_volume_m3=rail_volume,
        crossmembers=dict(count=count,pitch_m=actual_pitch,length_m=r['crossmember_length_m'],outside_m=[b,h],wall_m=t,area_m2=area,I_m4=I,mass_kg=crossmass),
        baseplates=dict(count=count*r['baseplates_per_crossmember'],size_m=r['baseplate_m'],mass_kg=platemass),
        anchors=dict(count=count*r['baseplates_per_crossmember']*r['anchors_per_baseplate'],diameter_m=r['anchor_diameter_m'],concrete_breakout_qualified=False,net_steel_mass_not_included=True),
        risers=dict(count=4*count,maximum_length_m=max(riser_lengths),outside_m=[postx,posty],wall_m=postwall,mass_kg=riser_mass),riser_caps_mass_kg=capsmass,support_parts=support_parts,
        steel_mass_kg=rail_mass+all_support_mass,old_flat_rail_steel_reused=False,
        vehicle_swept_clearance_fitted=False,rail_to_crossmember_connection_fitted=False,
        concrete_web_blockouts_qualified=False,
        scope='Four continuous L-return rail sections are counted from the magnetic candidate; new RHS crossmembers/baseplates carry them to beam webs. Joint gap/fringing, rail fastening, concrete breakout and tolerance remain holds; anchor/rail bolt mass is not yet net-designed.')


def _simple_beam(loads,L,x):
    """Point loads + separate uniform load; exact equilibrium at arbitrary x."""
    points,w=loads;R=sum(P*(L-p)/L for p,P in points)+w*L/2
    M=np.asarray([R*xx-w*xx*xx/2-sum(P*(xx-p) for p,P in points if p<xx) for xx in x])
    V=np.asarray([R-w*xx-sum(P for p,P in points if p<xx) for xx in x])
    right=sum(P for p,P in points)+w*L-R
    return R,right,M,V


def moving_envelope(candidate,loads,span_m=25.,dead_n_m=0.,step_m=.25):
    """Exact module point forces scanned across one candidate-specific span."""
    if not _finite(step_m) or not 0<step_m<=1:raise ValueError('bounded moving-load step required')
    L=span_m;x=np.linspace(0,L,201);cars=candidate['cars'];pitch=load()['loads']['car_pitch_m'];case=next(c for c in loads['cases'] if c['id']=='AW3-vertical-dynamic')
    # Train coordinate origin is the rear car centre; translate through every
    # module entering/leaving the span. Preserve actual asymmetric forces.
    train=[(car*pitch+m['at_m'][0],m['force_n'][2],m['at_m'][1]) for car in range(cars) for m in case['modules']]
    earliest=min(p for p,F,y in train);latest=max(p for p,F,y in train);offsets=np.arange(-latest,L-earliest+step_m/2,step_m)
    result=dict(max_moment_nm=0.,max_live_moment_nm=0.,max_shear_n=0.,max_end_reaction_n=0.,max_torsion_nm=0.,max_live_deflection_times_EI_n_m3=0.,critical_points=[],critical_offset_m=None)
    for offset in offsets:
        active=[(p+offset,F,y) for p,F,y in train if 0<=p+offset<=L];pts=[(p,F) for p,F,y in active]
        left,right,M,V=_simple_beam((pts,dead_n_m),L,x);live=_simple_beam((pts,0.),L,x)[2]
        peak=float(np.max(M));torque=abs(sum(F*y for p,F,y in active))
        if peak>result['max_moment_nm']:result.update(max_moment_nm=peak,critical_points=[dict(x_m=p,force_n=F,y_m=y) for p,F,y in active],critical_offset_m=float(offset),critical_moment_samples_nm=M.tolist())
        result['max_live_moment_nm']=max(result['max_live_moment_nm'],float(np.max(live)))
        result['max_shear_n']=max(result['max_shear_n'],float(np.max(np.abs(V))))
        result['max_end_reaction_n']=max(result['max_end_reaction_n'],left,right)
        result['max_torsion_nm']=max(result['max_torsion_nm'],torque)
        v=np.zeros_like(x)
        for p,P in pts:
            left=x<=p;v[left]+=P*(L-p)*x[left]*(L*L-(L-p)**2-x[left]**2)/(6*L)
            right=~left;v[right]+=P*p*(L-x[right])*(L*L-p*p-(L-x[right])**2)/(6*L)
        result['max_live_deflection_times_EI_n_m3']=max(result['max_live_deflection_times_EI_n_m3'],float(np.max(v)))
    # Torsion cannot disappear because the primary vertical scan is symmetric.
    # Apply two candidate asymmetric car wrenches to the span as a bounded
    # torsion envelope; local load sharing along the rail remains unverified.
    result['max_torsion_nm']=max(result['max_torsion_nm'],2*max(abs(c['target_wrench'][3]) for c in loads['cases']))
    result.update(x_samples_m=x.tolist(),scan_step_m=step_m,positions=len(offsets),span_m=L,dead_udl_n_m=dead_n_m,
        equilibrium_control=dict(point_midspan_reactions_n=[.5,.5],point_midspan_moment_per_n_m=L/4,udl_moment_per_n_m=L*L/8),
        scope='Candidate six-car module force pattern scanned at0.25m; exact point-load equilibrium per placement. Scan discretisation and simply supported single-span/static factors do not validate train-track dynamics or continuous guideway behavior.')
    return result


def strand_coordinates(section,bottom_count,top_count,a=None):
    a=load() if a is None else a;c=a['concrete'];b=section['width_m'];h=section['depth_m'];tf=section['flange_m'];d=c['strand_diameter_m'];edge=c['cover_m']+d/2
    pitch=d+c['strand_clearance_m'];slots=math.floor((b-2*edge)/pitch)+1
    if slots<2:raise ValueError('strand cover/spacing leaves no layout')
    rows=[]
    for location,count in (('bottom',bottom_count),('top',top_count)):
        layers=math.ceil(count/slots)
        if edge+(layers-1)*c['strand_vertical_pitch_m']+d/2>tf-c['cover_m']:return None
        remain=count
        for layer in range(layers):
            n=min(slots,remain);remain-=n
            for i in range(n):
                y=(i-(n-1)/2)*pitch;z=edge+layer*c['strand_vertical_pitch_m'];z=z if location=='bottom' else h-z
                rows.append(dict(id=f'{location}/{layer}/{i}',y_m=y,z_m=z,area_m2=c['strand_area_m2'],location=location))
    return rows


def _handling_moment(w,L,support_fraction):
    support=support_fraction*L;R=w*L/2;x=np.linspace(0,L,201)
    moments=[-w*xx*xx/2+(R*(xx-support) if xx>support else 0)+(R*(xx-(L-support)) if xx>L-support else 0) for xx in x]
    return min(moments),max(moments)


def prestress_design(section,envelope,dead_n_m,a=None):
    a=load() if a is None else a;c=a['concrete'];L=c['span_m'];sp=section_properties(section);area=sp['area_m2'];Z=sp['Z_m3'];h=section['depth_m'];trials=[]
    # Transfer/handling checks use actual strand forces and positions. Debonded
    # strands develop after their declared debond and transfer lengths.
    for nb in c['prestress_bottom_counts']:
        for nt in c['prestress_top_counts']:
            coords=strand_coordinates(section,nb,nt,a)
            if coords is None:continue
            for debond in c['prestress_debond_counts']:
                if debond>nb:continue
                stages=[];initial=c['strand_area_m2']*c['strand_strength_pa']*c['strand_initial_stress_fraction']
                for stage,kind,factor,loss in [('release','overhang',1.,0.),('lifting','overhang',a['construction']['handling_dynamic_factor'],0.),('transport','transport',a['construction']['transport_dynamic_factor'],0.),('service','service',1.,c['prestress_loss_fraction'])]:
                    stresses=[];limits=c['transfer_strength_pa']*c['transfer_compression_fraction'] if stage!='service' else c['strength_pa']*c['service_compression_fraction']
                    tensile=c['transfer_tension_screen_pa'] if stage!='service' else c['service_tension_screen_pa']
                    for xx in np.linspace(0,L,51):
                        if kind=='service':
                            p=[(r['x_m'],r['force_n']) for r in envelope['critical_points']];M=float(_simple_beam((p,dead_n_m),L,[xx])[2][0])
                        else:
                            frac=a['construction']['transport_support_fraction'] if kind=='transport' else a['construction']['lifting_support_fraction']
                            s=frac*L;w=dead_n_m*factor;R=w*L/2
                            M=-w*xx*xx/2+(R*(xx-s) if xx>s else 0)+(R*(xx-(L-s)) if xx>L-s else 0)
                        Ps=0.;Pe=0.;bottom_seen=0
                        for strand in coords:
                            start=0.
                            if strand['location']=='bottom':
                                if bottom_seen<debond:start=c['end_debond_length_m']
                                bottom_seen+=1
                            transfer=max(0.,min(1.,(min(xx,L-xx)-start)/c['strand_transfer_length_m']))
                            P=initial*(1-loss)*transfer;Ps+=P;Pe+=P*(h/2-strand['z_m'])
                        top=Ps/area-Pe/Z+M/Z;bottom=Ps/area+Pe/Z-M/Z
                        stresses.extend([top,bottom])
                    arithmetic=c['arithmetic_residual_pa']
                    stages.append(dict(id=stage,maximum_compression_pa=max(stresses),minimum_compression_pa=min(stresses),compression_limit_pa=limits,tensile_limit_pa=-tensile,
                        arithmetic_residual_pa=arithmetic,passed=bool(max(stresses)<=limits+arithmetic and min(stresses)>=-tensile-arithmetic)))
                # An independently imposed accidental capture envelope is kept
                # apart from ordinary live demand and cannot be hidden by a pass.
                totalP=initial*(nb+nt)*(1-c['prestress_loss_fraction']);ecc=sum(initial*(1-c['prestress_loss_fraction'])*(h/2-s['z_m']) for s in coords)/totalP
                accidental=envelope['max_moment_nm']*1.25;accstress=[totalP/area-totalP*ecc/Z+accidental/Z,totalP/area+totalP*ecc/Z-accidental/Z]
                Aps=(nb+nt)*c['strand_area_m2'];z=.8*h;resistance=Aps*.8*c['strand_strength_pa']*z
                ratio=max(max(r['maximum_compression_pa']/r['compression_limit_pa'],max(0.,-r['minimum_compression_pa'])/(max(1.,-r['tensile_limit_pa']))) for r in stages)
                passed=all(r['passed'] for r in stages) and resistance>=a['loads']['load_factor_dead']*dead_n_m*L*L/8+a['loads']['load_factor_live']*envelope['max_live_moment_nm']
                trials.append(dict(bottom_count=nb,top_count=nt,debond_count=debond,strand_coordinates=coords,stages=stages,maximum_screen_ratio=ratio,
                    effective_prestress_n=totalP,eccentricity_m=ecc,flexural_resistance_screen_nm=resistance,accidental_stress_pa=accstress,
                    accidental_load_factor=1.25,accidental_scope='Sensitivity only; capture point forces and contact torsion require coupled nonlinear verification.',passed=bool(passed)))
    if not trials:return dict(state='no-fit',passed=False,trials=0,reason='Strands cannot fit cover/spacing/flange thickness',selected=None)
    feasible=[r for r in trials if r['passed']];best=min(feasible or trials,key=lambda r:((0 if r['passed'] else r['maximum_screen_ratio']),r['bottom_count']+r['top_count'],r['debond_count']))
    return dict(state='screen-pass' if feasible else 'rejected',passed=bool(feasible),trials=len(trials),feasible_count=len(feasible),selected=best,
        prestress_layouts=[dict(bottom_count=r['bottom_count'],top_count=r['top_count'],debond_count=r['debond_count'],passed=r['passed'],maximum_screen_ratio=r['maximum_screen_ratio']) for r in trials],
        hold='End-zone bursting/spalling, strand anchorage/debond procedure, loss/creep/shrinkage, ductility/strain compatibility, fatigue and development require qualified detailed design.')


def _bar_mass(d,length,count=1):return math.pi*d*d/4*length*count*7850


def crane_alternative(gross_mass_kg,a=None):
    a=load() if a is None else a;r=a['larger_crane_reference'];radius=a['construction']['crane_radius_m'];rigging=a['construction']['lift_rigging_mass_kg'];total=gross_mass_kg+rigging+r['hook_block_kg']
    # The26m published row is used as a conservative upper-radius envelope for
    # a25m lift. Never interpolate a larger capacity from the24m row.
    valid_radius=0<radius<=r['chart_radius_m'];headheight=math.sqrt(max(0.,r['boom_m']**2-radius**2))
    requiredheight=a['pier']['height_m']+a['pier']['cap_size_m'][2]+2.5+6.
    return dict(id=r['id'],required_radius_m=radius,used_chart_radius_m=r['chart_radius_m'],boom_m=r['boom_m'],ballast_t=r['ballast_t'],
        girder_kg=gross_mass_kg,slings_and_spreader_kg=rigging,hook_block_kg=r['hook_block_kg'],chart_load_kg=total,capacity_kg=r['chart_capacity_kg'],
        radius_capacity_screen_pass=valid_radius and total<=r['chart_capacity_kg'],geometric_hook_height_m=headheight,required_hook_height_assumption_m=requiredheight,
        height_screen_pass=headheight>=requiredheight,manufacturer_max_outrigger_reaction_n=r['manufacturer_max_outrigger_reaction_n'],
        mat_area_sensitivities=[dict(soil=s['id'],assumed_allowable_pa=s['allowable_bearing_pa'],minimum_area_m2=r['manufacturer_max_outrigger_reaction_n']/s['allowable_bearing_pa'],
            square_side_m=math.sqrt(r['manufacturer_max_outrigger_reaction_n']/s['allowable_bearing_pa']),ground_and_mat_structural_design_approved=False) for s in a['soil_scenarios']],
        allocated_hire_planning_usd_per_span=(r['setup_days']+r['campaign_lift_days'])*r['daily_hire_planning_usd']/r['campaign_span_count'],
        price_is_quote=False,supplier_approved=False,source=dict(url=r['url'],document_sha256=r['document_sha256'],printed_chart_page=r['table_page_printed'],accessed=r['accessed']),scope=r['scope'])


def beam_design(candidate,loads,rail,a=None):
    a=load() if a is None else a;c=a['concrete'];L=c['span_m'];g=a['loads']['gravity_m_s2'];rows=[]
    for sec in a['beam_sections']:
        sp=section_properties(sec);b=sec['width_m'];h=sec['depth_m'];tw=sec['web_m'];tf=sec['flange_m']
        infill=(b-2*tw)*(h-2*tf)*2*c['end_block_length_m'];volume=sp['area_m2']*L+infill;concrete_mass=volume*c['density_kg_m3']
        # Reinforcement weight feeds the next dead-load iteration, not a hidden
        # post-analysis addition. Iterate count-based cages to a fixed quantity.
        cc=loads['capture'];capture_case=dict(id='AW3-vertical-dynamic',modules=[dict(at_m=p,force_n=f) for p,f in zip(cc['points_m'],cc['forces_n'])],target_wrench=cc['target_wrench'])
        rebarmass=0.;strandmass=0.;previous=None
        for iteration in range(5):
            dead=(concrete_mass+rail['steel_mass_kg']+rebarmass+strandmass)*g/L;envelope=moving_envelope(candidate,loads,L,dead);capture_envelope=moving_envelope(candidate,dict(cases=[capture_case]),L,dead)
            z=.8*h;Ak=sp['torsion_midline_area_m2'];required=max(max(envelope['max_shear_n'],capture_envelope['max_shear_n'])/(z*c['rebar_design_stress_pa']),envelope['max_torsion_nm']/(2*Ak*c['rebar_design_stress_pa']))
            d=.012;legarea=2*math.pi*d*d/4;pitches=[.10,.125,.15,.20,.25];pitch=max([p for p in pitches if legarea/p>=required] or [.10])
            count=math.ceil(L/pitch)+1;cut=2*(b-2*c['cover_m']+h-2*c['cover_m'])+20*d
            stirrupmass=_bar_mass(d,cut,count);longmass=_bar_mass(.016,L,8);endmass=_bar_mass(.016,2*(b+h),16)
            newrebar=stirrupmass+longmass+endmass;ps=prestress_design(sec,envelope,dead,a)
            selected=ps['selected'];newstrand=0 if selected is None else (selected['bottom_count']+selected['top_count'])*L*c['strand_area_m2']*7850
            totals=(round(newrebar,6),round(newstrand,6))
            rebarmass,strandmass=newrebar,newstrand
            if totals==previous:break
            previous=totals
        dead=(concrete_mass+rail['steel_mass_kg']+rebarmass+strandmass)*g/L;envelope=moving_envelope(candidate,loads,L,dead)
        capture_envelope=moving_envelope(candidate,dict(cases=[capture_case]),L,dead)
        # Maximum live deflection integrates the retained exact critical pattern
        # and explicitly reports the uncracked elastic section assumption.
        points=[(r['x_m'],r['force_n']) for r in envelope['critical_points']];xx=np.linspace(0,L,501);M=_simple_beam((points,0),L,xx)[2]
        curv=M/(c['young_pa']*sp['I_m4']);dx=L/(len(xx)-1);slope=np.r_[0,np.cumsum((curv[1:]+curv[:-1])*.5*dx)];v=np.r_[0,np.cumsum((slope[1:]+slope[:-1])*.5*dx)];v-=xx*v[-1]/L
        deflection=envelope['max_live_deflection_times_EI_n_m3']/(c['young_pa']*sp['I_m4'])
        grossmass=concrete_mass+rail['steel_mass_kg']+rebarmass+strandmass
        con=a['construction'];lift=_handling_moment(dead*con['handling_dynamic_factor'],L,con['lifting_support_fraction']);transport=_handling_moment(dead*con['transport_dynamic_factor'],L,con['transport_support_fraction'])
        chart=dict(zip(con['crane_chart_radii_m'],con['crane_chart_capacities_kg']));capacity=chart.get(con['crane_radius_m']);suspended=grossmass+con['lift_rigging_mass_kg']
        rollmoment=(grossmass*g*(con['transverse_sweep_assumption_m']+h/2*con['transport_crossfall'])+a['loads']['wind_pressure_pa']*h*L*h/2)
        restoring=grossmass*g*con['transport_support_width_m']/2;temporary_restoring=grossmass*g*con['temporary_bearing_width_m']/2
        support=rail['crossmembers'];modulepeak=max(m['force_n'][2] for cc in loads['cases'] for m in cc['modules']);cantilever=max(0.,1.28-b/2)
        bracketM=modulepeak*cantilever;crossstress=bracketM*(a['rail_support']['crossmember_depth_m']/2)/support['I_m4']
        stirrup_capacity=legarea/pitch*z*c['rebar_design_stress_pa'];torsionstress=envelope['max_torsion_nm']/(2*Ak*min(tw,tf))
        cost=volume*a['rates']['concrete_usd_m3']+rebarmass*a['rates']['fabricated_rebar_usd_kg']+strandmass*a['rates']['prestress_strand_usd_kg']+rail['steel_mass_kg']*a['rates']['fabricated_structural_steel_usd_kg']+2*L*(b+h)*a['rates']['formwork_usd_m2']
        larger=crane_alternative(grossmass,a);capture_stresses=[]
        if ps['selected']:
            sel=ps['selected'];P=sel['effective_prestress_n'];ecc=sel['eccentricity_m'];Mcap=capture_envelope['max_moment_nm'];capture_stresses=[P/sp['area_m2']-P*ecc/sp['Z_m3']+Mcap/sp['Z_m3'],P/sp['area_m2']+P*ecc/sp['Z_m3']-Mcap/sp['Z_m3']]
        capture_pass=bool(capture_stresses and min(capture_stresses)>=-c['arithmetic_residual_pa'] and max(capture_stresses)<=c['strength_pa']*c['service_compression_fraction']+c['arithmetic_residual_pa'])
        rows.append(dict(id=sec['id'],section=sec,properties=sp,concrete_volume_m3=volume,end_infill_volume_m3=infill,concrete_mass_kg=concrete_mass,
            reaction_rail_and_attachment_steel_mass_kg=rail['steel_mass_kg'],reinforcement_mass_kg=rebarmass,strand_mass_kg=strandmass,gross_mass_kg=grossmass,
            dead_load_n_m=dead,moving_load=envelope,capture_moving_load=capture_envelope,prestress=ps,
            capture_stress_screen=dict(face_stresses_pa=capture_stresses,passed=capture_pass,force_capability_qualified=False,scope='Independent moving8shoe energy-average pattern. Actual50k shoe rating failure remains separate; no clipped force is used to make the concrete screen pass.'),
            reinforcement=dict(stirrups=dict(diameter_m=d,pitch_m=pitch,count=count,cut_length_m=cut,mass_kg=stirrupmass),longitudinal=dict(diameter_m=.016,count=8,length_m=L,mass_kg=longmass),end_bursting_allocation=dict(diameter_m=.016,count=16,cut_length_m=2*(b+h),mass_kg=endmass),
                shear_capacity_screen_n=stirrup_capacity,torsion_shear_stress_pa=torsionstress,anchorage_and_crack_width_qualified=False),
            deflection=dict(live_m=deflection,limit_m=L/c['beam_live_deflection_divisor'],passed=deflection<=L/c['beam_live_deflection_divisor'],scope='Uncracked elastic simply supported integration; rail dynamics/cracking/effective stiffness excluded.'),
            rail_crossmember=dict(moment_nm=bracketM,stress_pa=crossstress,passed=crossstress<=a['steel']['stress_screen_pa'],concrete_anchor_breakout_qualified=False),
            construction=dict(lift_supports_x_m=[con['lifting_support_fraction']*L,(1-con['lifting_support_fraction'])*L],lifting_moment_range_nm=list(lift),transport_moment_range_nm=list(transport),
                transport_roll_moment_nm=rollmoment,transport_restoring_nm=restoring,transport_static_roll_screen_pass=restoring>rollmoment,temporary_bearing_restoring_nm=temporary_restoring,
                temporary_brace_count=math.ceil(L/con['temporary_brace_pitch_m'])+1,temporary_brace_force_screen_n=con['temporary_brace_force_screen_n'],
                crane=dict(radius_m=con['crane_radius_m'],capacity_kg=capacity,suspended_mass_kg=suspended,screen_pass=capacity is not None and suspended<=capacity,supplier_approved=False),
                larger_crane_alternative=larger,
                handling_girder_lateral_stability_qualified=False,transport_route_approved=False,
                scope='Exact counted gross lift including reinforcement/rails and rigging. Static roll is only a control, not the WSDOT/PCI imperfect-girder lateral stability method or a signed crane chart.'),
            quantity_iteration_count=iteration+1,material_and_formwork_cost_usd=cost,price_is_quote=False,
            passed_implemented_screens=bool(ps['passed'] and capture_pass and deflection<=L/c['beam_live_deflection_divisor'] and crossstress<=a['steel']['stress_screen_pa'] and stirrup_capacity>=max(envelope['max_shear_n'],capture_envelope['max_shear_n']) and capacity is not None and suspended<=capacity),
            accepted=False))
    return rows


def dynamics_properties(candidate=None,section_id='narrow-deep-reference'):
    """Uncracked first-mode contract for a separate flexible-guideway solver.

    This exports the exact counted trial section, not a tuned inertia. A caller
    must retain cracking/joint/bearing/rail-connection uncertainty and return its
    calculated moving forces to the structural load exporter.
    """
    from . import candidate_magnetics
    candidate=candidate_magnetics.definition() if candidate is None else candidate;a=load();a['beam_sections']=[s for s in a['beam_sections'] if s['id']==section_id]
    if len(a['beam_sections'])!=1:raise ValueError('declared structural section required')
    mass=mass_properties(candidate,a);loads=load_cases(candidate,mass,a);rail=return_rail_and_attachments(candidate,a=a);beam=beam_design(candidate,loads,rail,a)[0];sp=beam['properties'];L=a['concrete']['span_m'];E=a['concrete']['young_pa'];nu=.20
    # Concrete centroid is the reference for the polar mass; actual return
    # sections use their exact y/z placement. RHS/baseplate distribution is a
    # disclosed envelope approximation until its fitted support definition.
    zc=a['rail_support']['beam_top_z_m']-beam['section']['depth_m']/2;polar=a['concrete']['density_kg_m3']*(sp['I_m4']+sp['weak_I_m4'])
    for p in rail['guideway']['parts']:
        m=p['mass_kg']/L;size=p['size_m'];cg=p['cg_m'];polar+=m*((size[1]**2+size[2]**2)/12+cg[1]**2+(cg[2]-zc)**2)
    polar+=(beam['reinforcement_mass_kg']+beam['strand_mass_kg'])/L*(beam['section']['depth_m']/2)**2
    polar+=(rail['crossmembers']['mass_kg']+rail['baseplates']['mass_kg'])/L*(1.45**2+(a['rail_support']['beam_top_z_m']-zc)**2)
    return dict(configuration_sha256=candidate['configuration_sha256'],section_id=section_id,span_m=L,young_pa=E,shear_pa=E/(2*(1+nu)),poisson_assumption=nu,
        area_m2=sp['area_m2'],vertical_inertia_m4=sp['I_m4'],lateral_inertia_m4=sp['weak_I_m4'],torsion_constant_m4=sp['torsion_J_m4'],
        distributed_mass_kg_m=beam['gross_mass_kg']/L,polar_mass_per_length_kg_m=polar,beam_centroid_z_m=zc,
        reinforcement_mass_kg=beam['reinforcement_mass_kg'],strand_mass_kg=beam['strand_mass_kg'],new_rail_support_mass_kg=rail['steel_mass_kg'],
        assumptions=['Uncracked concrete E34GPa,Poisson0.20; no prestress geometric stiffness, cracking or creep reduction.',
            'Simply supported25m section; real bearing/rail joints, torsion warping and concrete attachment stiffness unqualified.',
            'Support RHS/baseplate polar inertia is an explicit envelope until fitted support geometry; all steel mass counted.',
            'Eigenmodes/control response require coupled simulation; this API conveys inputs, not a dynamic pass.'],qualified=False,**FLAGS)


def bearing_design(beam,loads,a=None):
    a=load() if a is None else a;b=a['bearings'];L=a['concrete']['span_m'];pad=b['pad_m'];spacing=b['transverse_centre_spacing_m'];V=max(beam['moving_load']['max_end_reaction_n'],beam['capture_moving_load']['max_end_reaction_n'])
    # Each girder end has two actual pads. Include the largest asymmetric
    # candidate roll wrench; two cars can load the25m span at once.
    roll=max(abs(c['target_wrench'][3]) for c in loads['cases'])*2
    endT=roll/2;padforces=[V/2-endT/spacing,V/2+endT/spacing]
    movement=L*b['thermal_expansion_per_k']*b['thermal_range_k']+b['shrinkage_movement_allowance_m'];maxcompression=max(padforces)/(pad[0]*pad[1])
    braking=max(abs(c['target_wrench'][0]) for c in loads['cases'])*2
    anchors=b['fixed_anchor_count_per_end'];As=b['anchor_thread_area_m2'];shear=braking/anchors
    anchorcapacity=As*a['steel']['bolt_shear_screen_pa'];uplift=max(0.,-min(padforces));tension=uplift/(anchors/2)
    return dict(id=beam['id']+'/bearings',count_per_beam=4,pad_m=pad,centres_at_each_end_y_m=[-spacing/2,spacing/2],maximum_end_reaction_n=V,
        imposed_roll_torque_nm=roll,torque_at_each_end_nm=endT,pad_forces_n=padforces,compression_peak_pa=maxcompression,compression_limit_pa=b['compression_screen_pa'],
        transverse_footprint_m=spacing+pad[0],fits_concrete_width=spacing+pad[0]<=beam['section']['width_m'],
        movement_required_m=movement,movement_capacity_m=b['movement_capacity_m'],fixed_anchors_per_end=anchors,anchor_shear_n=shear,anchor_shear_capacity_n=anchorcapacity,
        anchor_tension_n=tension,anchor_concrete_breakout_qualified=False,elastomer_rotation_creep_qualified=False,
        passed_implemented_screens=bool(min(padforces)>=0 and maxcompression<=b['compression_screen_pa'] and movement<=b['movement_capacity_m'] and shear<=anchorcapacity and spacing+pad[0]<=beam['section']['width_m']),
        material_budget_usd=4*a['rates']['bearing_usd_unit'],accepted=False,
        scope='One pair at each beam end with explicit roll couple and two-car braking. Pad pressure/movement and anchor steel only; bearing rotation, fatigue, anchorage/concrete breakout and actual fixed/guided layout remain holds.')


def substructure_design(beam,bearing,loads,a=None):
    a=load() if a is None else a;p=a['pier'];f=a['foundations'];g=a['loads']['gravity_m_s2'];c=a['concrete'];rates=a['rates'];H=p['height_m'];capV=math.prod(p['cap_size_m']);capmass=capV*c['density_kg_m3'];rows=[]
    # One intermediate pier supports left+right spans on each of two fixed
    # lines. Per direction deadweight is one full span; live reactions are
    # independent, so asymmetry cannot vanish through a symmetry assumption.
    deadbeam=beam['gross_mass_kg']*g;end=bearing['maximum_end_reaction_n'];liveEnd=max(0.,end-deadbeam/2)
    vertical=2*deadbeam+4*liveEnd
    differential=2*liveEnd*max(abs(x) for x in p['guideway_centres_y_m'])
    brake_car=max(abs(case['target_wrench'][0]) for case in loads['cases']);distributed_brake=2*brake_car
    fulltrain_brake=6*brake_car
    wind=a['loads']['wind_pressure_pa']*(a['loads']['car_length_m']*2.5*2+p['height_m']*2.)
    # Seismic horizontal coefficient is an analyst scenario; not a Baghdad
    # site spectrum. Include all tributary beam/live weight and cap/column.
    for D in p['outer_diameters_m']:
        di=D*p['inner_to_outer_ratio'];A=math.pi*(D*D-di*di)/4;I=math.pi*(D**4-di**4)/64
        colV=A*H;colmass=colV*c['density_kg_m3'];N=vertical+(colmass+capmass)*g
        seismic=N*a['loads']['seismic_horizontal_acceleration_fraction_g'];lateral=max(wind,seismic)
        Mx=differential+lateral*H;My=distributed_brake*H;Madverse=fulltrain_brake*H
        Pcr=math.pi**2*c['young_pa']*I/(p['effective_length_factor']*H)**2
        amp=1/(1-N/Pcr) if N<Pcr else 1e12
        As=p['longitudinal_bars']*math.pi*p['longitudinal_bar_diameter_m']**2/4
        axialcap=.4*c['strength_pa']*A;Mcap=.5*As*c['rebar_design_stress_pa']*.75*D
        normal=max(abs(Mx),abs(My))*amp;util=N/axialcap+normal/Mcap
        adverseutil=N/axialcap+max(abs(Mx),abs(Madverse))*amp/Mcap
        longmass=_bar_mass(p['longitudinal_bar_diameter_m'],H+2.,p['longitudinal_bars']);hoops=math.ceil(H/p['hoop_pitch_m'])+1
        hooplength=math.pi*(D-2*c['cover_m'])+math.pi*(di+2*c['cover_m'])+40*p['hoop_diameter_m']
        hoopmass=_bar_mass(p['hoop_diameter_m'],hooplength,hoops)
        # A counted cap cage; strut/tie nodes and bearing-seat local zones are
        # explicitly unqualified, rather than silently called designed.
        caplong=_bar_mass(.025,p['cap_size_m'][1],32);caplinks=_bar_mass(.016,2*(p['cap_size_m'][0]+p['cap_size_m'][2]-.20)+.32,math.ceil(p['cap_size_m'][1]/.125)+1)
        rebar=longmass+hoopmass+caplong+caplinks
        cost=(colV+capV)*rates['concrete_usd_m3']+rebar*rates['fabricated_rebar_usd_kg']+(math.pi*(D+di)*H+2*p['cap_size_m'][1]*(p['cap_size_m'][0]+p['cap_size_m'][2]))*rates['formwork_usd_m2']
        foundations=[]
        for soil in a['soil_scenarios']:
            scenario=[]
            for B in f['spread_sides_m']:
                depth=f['spread_depth_m'];vol=B*B*depth;weight=vol*soil['effective_concrete_unit_weight_n_m3'];V=N+weight
                # Biaxial corners, no-tension. Units N/m² throughout.
                q0=V/(B*B);dq=6*(abs(Mx)+abs(My))*amp/B**3;qmax=q0+dq;qmin=q0-dq
                Hforce=math.hypot(distributed_brake,lateral);slide=Hforce/(f['friction_coefficient_assumed']*V)
                effective=depth-c['cover_m']-.016;arm=(B-D)/2;momentstrip=max(0.,qmax)*arm**2/2
                Asm=max(.0013*effective,momentstrip/(.85*effective*c['rebar_design_stress_pa']));bar=.020;spacing=min(.20,math.pi*bar*bar/4/Asm)
                count=math.ceil(B/spacing)+1;cut=B-2*c['cover_m']+.8;kg=_bar_mass(bar,cut,count*4)
                perimeter=math.pi*(D+effective);punch=max(0.,N-q0*math.pi*(D+effective)**2/4)/(perimeter*effective)
                passed=qmin>=0 and qmax<=soil['allowable_bearing_pa'] and slide<=1 and punch<=f['punching_shear_screen_pa']
                cash=vol*rates['concrete_usd_m3']+kg*rates['fabricated_rebar_usd_kg']+B*B*(depth+.5)*rates['excavation_usd_m3']+4*B*depth*rates['formwork_usd_m2']
                scenario.append(dict(id=f"{soil['id']}/spread-{B:g}",type='spread',side_m=B,depth_m=depth,concrete_m3=vol,rebar_kg=kg,
                    cage=dict(diameter_m=bar,bars_per_direction_per_face=count,faces=2,cut_length_m=cut,actual_pitch_m=B/(count-1)),
                    qmax_pa=qmax,qmin_pa=qmin,allowable_pa=soil['allowable_bearing_pa'],sliding_utilisation=slide,punching_stress_pa=punch,
                    passed_implemented_screens=bool(passed),material_excavation_formwork_cost_usd=cash,old_foundation_allowance_usd=rates['foundation_old_allowance_usd'],settlement_qualified=False,soil_values_measured=False,accepted=False))
            d=f['pile_diameter_m'];Ag=math.pi*d*d/4;spacing=d*f['pile_spacing_diameters']
            for grid in f['pile_grid_counts']:
                n=grid*grid;B=(grid-1)*spacing+2*d;capdepth=f['pile_cap_depth_m'];capvol=B*B*capdepth;capweight=capvol*soil['effective_concrete_unit_weight_n_m3']
                coords=[((i-(grid-1)/2)*spacing,(j-(grid-1)/2)*spacing) for i in range(grid) for j in range(grid)];s2=sum(x*x for x,y in coords)
                pileforces=[(N+capweight)/n+Mx*amp*y/s2+My*amp*x/s2 for x,y in coords]
                for length in f['pile_lengths_m']:
                    shaft=math.pi*d*length*soil['pile_shaft_screen_pa'];toe=Ag*soil['pile_base_screen_pa'];resistance=(shaft+toe)*f['pile_group_efficiency']
                    pilevol=n*Ag*length;steel=(pilevol+capvol)*f['pile_rebar_fraction']*a['steel']['density_kg_m3']
                    passed=max(pileforces)<=resistance and min(pileforces)>=0
                    cash=(pilevol+capvol)*rates['concrete_usd_m3']+steel*rates['fabricated_rebar_usd_kg']+n*length*rates['pile_drilling_usd_m']+B*B*(capdepth+.5)*rates['excavation_usd_m3']
                    scenario.append(dict(id=f"{soil['id']}/pile-{grid}x{grid}-{length:g}",type='piled',pile_diameter_m=d,pile_count=n,pile_length_m=length,
                        pile_centres_m=[list(x) for x in coords],pile_axial_forces_n=pileforces,shaft_plus_toe_screen_n=shaft+toe,group_efficiency=f['pile_group_efficiency'],resistance_per_pile_n=resistance,
                        pile_concrete_m3=pilevol,cap_concrete_m3=capvol,concrete_m3=pilevol+capvol,rebar_kg=steel,rebar_basis='1.5% volume planning cage; explicit pile/cap bar development design remains open',
                        cap_size_m=[B,B,capdepth],passed_implemented_screens=bool(passed),material_excavation_formwork_cost_usd=cash,soil_values_measured=False,
                        old_foundation_allowance_usd=rates['foundation_old_allowance_usd'],settlement_qualified=False,lateral_pile_capacity_qualified=False,accepted=False))
            possible=[x for x in scenario if x['passed_implemented_screens']]
            foundations.append(dict(soil=soil,alternatives=scenario,least_cost_screen_option=min(possible,key=lambda x:x['material_excavation_formwork_cost_usd']) if possible else None,
                interpretation='Unmeasured50/100/150kPa and shaft/toe sensitivity. ISRIC pedological maps do not provide these values; no site selection or foundation release.'))
        rows.append(dict(id=f'column-{D:g}',outer_diameter_m=D,inner_diameter_m=di,height_m=H,concrete_m3=colV+capV,cap_concrete_m3=capV,
            longitudinal_cage=dict(count=p['longitudinal_bars'],diameter_m=p['longitudinal_bar_diameter_m'],cut_length_m=H+2,mass_kg=longmass),
            hoops=dict(count=hoops,diameter_m=p['hoop_diameter_m'],cut_length_m=hooplength,mass_kg=hoopmass),cap_rebar_kg=caplong+caplinks,rebar_kg=rebar,
            vertical_n=N,normal_moments_nm=[Mx,My],full_train_braking_adverse_moment_nm=Madverse,seismic_horizontal_n=seismic,wind_n=wind,
            elastic_buckling_n=Pcr,second_order_factor=amp,axial_moment_utilisation=util,full_train_single_pier_braking_utilisation=adverseutil,
            passed_implemented_screens=util<=1,full_train_braking_distribution_qualified=False,cap_strut_tie_qualified=False,
            material_formwork_cost_usd=cost,old_column_cap_allowance_usd=rates['column_cap_old_allowance_usd'],foundations=foundations,accepted=False,
            scope='Equilibrium-derived biaxial N-M sensitivity and Euler amplification, not a reinforced-concrete interaction surface or ductile seismic design. Bearing-seat/cap nodes, shear, confinement, P-delta and connection details remain acceptance holds.'))
    return rows


def _drawings(value):
    """Dimension-driven repo-native sections; no AI concept rendering."""
    beam=value['civil']['beam_variants'][0];sec=beam['section'];scale=130;x0=400;y0=420;b=sec['width_m'];h=sec['depth_m'];tw=sec['web_m'];tf=sec['flange_m'];strands=[]
    selected=beam['prestress']['selected']
    if selected:
        for s in selected['strand_coordinates']:strands.append(f'<circle cx="{x0+s["y_m"]*scale:.2f}" cy="{y0-s["z_m"]*scale:.2f}" r="3" fill="#df7723"/>')
    title=f'Candidate {value["configuration_sha256"][:12]} | 25 m structural study'
    section=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="600" viewBox="0 0 1000 600"><rect width="1000" height="600" fill="#f6f8fa"/><g font-family="sans-serif" fill="#172d3d"><text x="30" y="35" font-size="22">{title}</text><text x="30" y="65" font-size="15">Provisional geometry and counted stock; no manufacturing or engineering release</text></g><rect x="{x0-b*scale/2}" y="{y0-h*scale}" width="{b*scale}" height="{h*scale}" fill="#bdc8d0" stroke="#172d3d"/><rect x="{x0-(b-2*tw)*scale/2}" y="{y0-(h-tf)*scale}" width="{(b-2*tw)*scale}" height="{(h-2*tf)*scale}" fill="#f6f8fa" stroke="#172d3d"/>{''.join(strands)}<g font-family="sans-serif" font-size="16" fill="#172d3d"><text x="550" y="130">Box {b:.3f} m × {h:.3f} m</text><text x="550" y="160">Web {tw:.3f} m; flange {tf:.3f} m</text><text x="550" y="190">Concrete {beam['concrete_volume_m3']:.3f} m³</text><text x="550" y="220">New return/support steel {beam['reaction_rail_and_attachment_steel_mass_kg']/1000:.2f} t</text><text x="550" y="250">Rebar {beam['reinforcement_mass_kg']:.0f} kg; strands {beam['strand_mass_kg']:.0f} kg</text><text x="550" y="280">Gross span {beam['gross_mass_kg']/1000:.2f} t</text><text x="30" y="485">Orange points: actual proposed strand coordinates; end zones/cages need detail approval.</text><text x="30" y="515">L-rails and transverse supports are counted separately from the concrete box.</text><text x="30" y="545">Soil, bearings, local anchors, rail joints, fatigue and dynamic coupling remain open.</text></g></svg>'''
    points=value['load_export']['cases'][1]['modules'];elements=[]
    for p in points:
        x=500+p['at_m'][0]*55;y=230-p['at_m'][1]*70
        elements.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#df7723"/><path d="M{x:.2f},{y+45:.2f}v-35" stroke="#126c74" stroke-width="2"/>')
    body=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="500"><rect width="1000" height="500" fill="#f6f8fa"/><g font-family="sans-serif" fill="#172d3d"><text x="25" y="35" font-size="22">Exact candidate load application / finished-floor frame</text><text x="25" y="65" font-size="16">24 attachments; six-car train; AW3 {value['controlled_aw3_kg']:.1f} kg per car</text></g><rect x="32.5" y="137.25" width="935" height="185.5" fill="#dde5e9" stroke="#172d3d"/>{''.join(elements)}<g font-family="sans-serif" font-size="16" fill="#172d3d"><text x="25" y="380">x: −8.5..+8.5 m; modules x: −5.5..+5.5 m; rows y: ±0.88 m.</text><text x="25" y="410">Forces and moments recovered by full6DOF equilibrium; no old26.4t load scaling.</text><text x="25" y="440">Rigid equal-compliance allocation only; control, flexibility and attachment qualification open.</text></g></svg>'''
    return {'beam-section.svg':section,'candidate-load-plan.svg':body}


def _bom(beams,substructures,bearings):
    rows=[]
    for beam in beams:
        prefix=beam['id'];rows.extend([
            dict(id=prefix+'/precast-box',unit='m3',quantity=beam['concrete_volume_m3'],material='45MPa concrete hypothesis',process='controlled precast, release strength and curing hold',drawing='beam-section.svg'),
            dict(id=prefix+'/reaction-rails-and-supports',unit='kg',quantity=beam['reaction_rail_and_attachment_steel_mass_kg'],material='candidate L-return steel and RHS/brackets',process='lamination cut/stack/joint + fabricated support; magnetic properties and anchors hold'),
            dict(id=prefix+'/reinforcement',unit='kg',quantity=beam['reinforcement_mass_kg'],material='435MPa design-stress hypothesis',process='cut/bend/fix cages; development and end-zone review hold'),
            dict(id=prefix+'/prestress',unit='kg',quantity=beam['strand_mass_kg'],material='15.2mm strand1860MPa hypothesis',process='pretension bed; calibrated jack, elongation, transfer/debond hold'),
            dict(id=prefix+'/bearings',unit='unit',quantity=4,material='elastomeric hypothesis',process='supplier pressure/rotation/movement/fatigue qualification hold')])
        for p in substructures[prefix]:
            rows.append(dict(id=prefix+'/'+p['id']+'/concrete',unit='m3',quantity=p['concrete_m3'],material='45MPa concrete hypothesis',process='precast hollow column + cap, connections held'))
            rows.append(dict(id=prefix+'/'+p['id']+'/cage',unit='kg',quantity=p['rebar_kg'],material='reinforcement hypothesis',process='counted bars/hoops, lap/anchorage/confinement hold'))
            for s in p['foundations']:
                for f in s['alternatives']:
                    rows.extend([dict(id=prefix+'/'+p['id']+'/'+f['id']+'/concrete',unit='m3',quantity=f['concrete_m3'],material='foundation concrete',process='scenario alternative, not additive with other foundations'),
                        dict(id=prefix+'/'+p['id']+'/'+f['id']+'/rebar',unit='kg',quantity=f['rebar_kg'],material='foundation reinforcement',process='scenario alternative, not additive with other foundations')])
    for row in rows:row.update(tolerance_approved=False,material_approved=False,manufacturing_release=False)
    return rows


def geometry_definition(value):
    """Counted representative physical units; alternatives are kept separate."""
    beam=value['civil']['beam_variants'][0];s=beam['section'];L=25.;b=s['width_m'];h=s['depth_m'];tw=s['web_m'];tf=s['flange_m'];top=value['assumptions']['rail_support']['beam_top_z_m'];bottom=top-h;parts=[]
    def add(uid,size,at,material):parts.append(dict(id=uid,kind='box',size_m=size,at_m=at,material=material,volume_m3=math.prod(size)))
    add('girder/bottom-flange',[L,b,tf],[-L/2,-b/2,bottom],'concrete')
    add('girder/top-flange',[L,b,tf],[-L/2,-b/2,top-tf],'concrete')
    for side in (-1,1):add(f'girder/web-{side}',[L,tw,h-2*tf],[-L/2,-b/2 if side<0 else b/2-tw,bottom+tf],'concrete')
    e=value['assumptions']['concrete']['end_block_length_m']
    for side in (-1,1):add(f'girder/end-infill-{side}',[e,b-2*tw,h-2*tf],[-L/2 if side<0 else L/2-e,-b/2+tw,bottom+tf],'concrete')
    parts.extend(value['civil']['rail_and_attachments']['guideway']['parts']);parts.extend(value['civil']['rail_and_attachments']['support_parts'])
    actual=sum(p['volume_m3'] for p in parts if p['material']=='concrete')
    if not math.isclose(actual,beam['concrete_volume_m3'],abs_tol=1e-9):raise ValueError('drawn concrete does not match counted section')
    return dict(schema='osr-candidate-structural-geometry/1',configuration_sha256=value['configuration_sha256'],parts=parts,
        prestress_coordinates=beam['prestress']['selected']['strand_coordinates'] if beam['prestress']['selected'] else [],
        reference_frame='x centred on25m span,y acrosssingletrainbeam,z fromvehiclefinishedfloor',
        net_manufactured_solids_complete=False,
        explicit_holds=['Fixed RHS crossmembers require engineered cast-in web blockouts/infill/anchors; concrete volume is gross conservative stock, not net Boolean concrete around steel.',
            'Rail joints, clips, anchors, rebar bends/hooks/strand terminations, local stiffeners and concrete cover tolerance require detailed native geometry.',
            'Section/topdatum is a proposed installation, not a surveyed Baghdad elevation.'],**FLAGS)


def _image(value):
    """Portable geometric pixel oracle; fonts and PNG encoding are not oracles."""
    from PIL import Image,ImageDraw
    image=Image.new('RGB',(1000,600),(246,248,250));draw=ImageDraw.Draw(image);beam=value['civil']['beam_variants'][0];s=beam['section'];scale=130;x0=400;y0=420
    b=s['width_m'];h=s['depth_m'];tw=s['web_m'];tf=s['flange_m']
    rect=lambda bb,fill:draw.rectangle(tuple(round(x) for x in bb),fill=fill)
    rect([x0-b*scale/2,y0-h*scale,x0+b*scale/2,y0],(189,200,208));rect([x0-(b-2*tw)*scale/2,y0-(h-tf)*scale,x0+(b-2*tw)*scale/2,y0-tf*scale],(246,248,250))
    selected=beam['prestress']['selected']
    if selected:
        for p in selected['strand_coordinates']:
            x=x0+p['y_m']*scale;y=y0-p['z_m']*scale;draw.ellipse([round(x-3),round(y-3),round(x+3),round(y+3)],fill=(223,119,35))
    # A proportional quantity chart is geometry-derived, not decorative AI.
    masses=[beam['concrete_mass_kg'],beam['reaction_rail_and_attachment_steel_mass_kg'],beam['reinforcement_mass_kg'],beam['strand_mass_kg']];colours=[(189,200,208),(23,45,61),(18,108,116),(223,119,35)]
    for i,(m,col) in enumerate(zip(masses,colours)):rect([560,120+i*70,560+350*m/max(masses),155+i*70],col)
    return image


def manufacturing_schedule(value):
    beam=value['civil']['beam_variants'][0];ps=beam['prestress']['selected'];n=0 if ps is None else ps['bottom_count']+ps['top_count'];a=value['assumptions']
    return dict(unit='one25mspan',configuration_sha256=value['configuration_sha256'],
        stages=[dict(id='CST-10',operation='cut/bend/trace cage and exact rail/support stock',predecessors=[],counted_rebar_kg=beam['reinforcement_mass_kg'],counted_structural_steel_kg=beam['reaction_rail_and_attachment_steel_mass_kg'],gate='approved detailing/materials and rail magnetic tests'),
            dict(id='CST-20',operation='set mould, cage, strand coordinates and anchor/blockout interfaces',predecessors=['CST-10'],strand_count=n,gate='cover/spacing/endzone independent design review'),
            dict(id='CST-30',operation='stress and cast',predecessors=['CST-20'],concrete_m3=beam['concrete_volume_m3'],stressing_bed_force_n=n*a['concrete']['strand_area_m2']*a['concrete']['strand_strength_pa']*a['concrete']['strand_initial_stress_fraction'],gate='jack calibration/elongation + mould/bed rating'),
            dict(id='CST-40',operation='cure, verify strength and transfer under approved sequence',predecessors=['CST-30'],release_strength_pa=a['concrete']['transfer_strength_pa'],gate='measured strength/curing, not elapsed time alone'),
            dict(id='CST-50',operation='fit rail stock/closures, survey and proof inspect',predecessors=['CST-40'],gate='gap/geometry/rail joints and magnetic acceptance'),
            dict(id='CST-60',operation='lift to transporter using declared supports/temporary restraints',predecessors=['CST-50'],lift_mass_kg=beam['gross_mass_kg'],gate='full lateral-stability and transport route/axle plan'),
            dict(id='CST-70',operation='erect on four approved bearings and complete anchors',predecessors=['CST-60'],bearing_count=4,gate='crane chart/radius/ground/rigging and surveyed pads'),
            dict(id='CST-80',operation='connect, inspect, survey and dynamic commissioning',predecessors=['CST-70'],gate='connection/geometry/physical tests and independent acceptance')],
        elapsed_duration_accepted=False,scope='Counted manufacturing and erection sequence. No production/curing/day rate or completed hold point is asserted.',**FLAGS)


def study(candidate=None):
    from . import candidate_magnetics
    before={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}
    a=load();candidate=validate_candidate(candidate_magnetics.definition() if candidate is None else deepcopy(candidate));mass=mass_properties(candidate,a);loads=load_cases(candidate,mass,a)
    mech=mechanical(candidate,mass,loads,a);rail=return_rail_and_attachments(candidate,a=a);beams=beam_design(candidate,loads,rail,a)
    bearings={b['id']:bearing_design(b,loads,a) for b in beams};substructures={b['id']:substructure_design(b,bearings[b['id']],loads,a) for b in beams}
    constraints=[]
    for c in loads['cases']:
        if not c['force_screen_pass']:constraints.append(dict(id='module-force/'+c['id'],state='failed',observed=c['peak_module_resultant_n'],limit=c['module_force_screen_n']))
    for uid,result in [('hardpoint',mech['hardpoint']),('collector-splice',mech['collector_splice']),('body-spine',mech['body_spine'])]:
        constraints.append(dict(id=uid,state='screen-pass' if result['passed'] else 'failed',accepted=False))
    for b in beams:constraints.append(dict(id='civil/'+b['id'],state='screen-pass' if b['passed_implemented_screens'] else 'failed',accepted=False))
    fixed_geometry=deepcopy(rail['guideway']);fixed_geometry['parts'].extend(rail['support_parts'])
    clearance=interface_clearance(candidate,fixed_geometry,a);constraints.append(dict(id='vehicle-return-interface',state='failed' if clearance['material_interference_count'] else 'hold',accepted=False))
    protection=protection_structures(candidate,mass,loads,a)
    for uid,passed in [('full-passive-capture',protection['capture']['unsupported_drop_screen_pass']),('downhill-brake-deceleration',protection['braking']['deceleration_screen_pass']),('downhill-brake-heat',protection['braking']['thermal_screen_pass'])]:constraints.append(dict(id=uid,state='screen-pass' if passed else 'failed',accepted=False))
    result=dict(schema=SCHEMA,configuration_sha256=candidate['configuration_sha256'],parent_configuration_sha256=candidate['parent_configuration_sha256'],candidate_id=candidate['id'],
        controlled_tare_kg=candidate['controlled_tare_kg'],controlled_aw3_kg=candidate['controlled_aw3_kg'],cars=candidate['cars'],
        assumptions=a,mass_properties=mass,load_export=loads,mechanical=mech,
        civil=dict(rail_and_attachments=rail,beam_variants=beams,bearings=bearings,substructure_variants=substructures),interface_clearance=clearance,
        preferred_static_support=preferred_support_loads(candidate),axial_properties=axial_properties(candidate),vehicle_handling=vehicle_handling(candidate,mass,a),protection_structures=protection,
        constraints=constraints,all_implemented_screens_pass=all(r['state']=='screen-pass' for r in constraints),
        physical_holds=['Measured as-built mass/CG/inertia and full load spectra; retained allocation placements and densities remain assumptions.',
            'Qualified material/coupon/weld/bond/fastener fatigue, full plate/contact/buckling and crash/capture tests.',
            'Complete flexible train-guideway controls/structural coupling, lateral/curve/terminal loop dynamics and loss/recovery contacts.',
            'Precast end-zone, prestress losses/transfer/development/ductility and local reaction-rail anchorage/joints/tolerances.',
            'Full girder handling lateral-stability, transport route, supplier crane chart/radius/rigging and ground plan.',
            'Site-specific boreholes/CPT, groundwater/chemistry/settlement/liquefaction/scour, seismic spectrum and competent design acceptance.',
            'Reinforced-concrete pier/cap interaction/shear/ductility, joints and pile group/lateral/settlement tests.',
            'No alternative stock is installed by this study. Geometry-changing alternatives require a new common identity, mass closure, native fit and repeated dynamics.'],
        qa_schedule=[dict(stage=stage,requirements=requirements,state='unexecuted',release=False) for stage,requirements in [
            ('design',['signed candidate-specific force/moment load envelope','independent joint/contact/shell and fatigue review','bar/strand/anchor tolerance and buildable drawings']),
            ('factory',['material/steel/ferrite/strand certificates','measured concrete release strength and curing','jack force/elongation/debond records','rail joint/lamination magnetic and dimensional tests']),
            ('handling',['approved lift points/inserts and girder lateral-stability','configuration-specific crane radius chart and ground pressure','transport survey and temporary restraints']),
            ('installed',['foundation verification/load tests','bearing/anchor installation and preload/torque records','rail geometry/joint surveys','dynamic commissioning and independent acceptance'])]],
        **FLAGS)
    result['bom']=_bom(beams,substructures,bearings)
    result['bom'].extend(dict(id=p['id'],unit='kg',quantity=p['mass_kg'],material='separate manufacturing lifting fixture',process='Counted external ten-fork frame; native fit, lugs, welds, unequal sharing and lift-plan qualification held',tolerance_approved=False,material_approved=False,manufacturing_release=False) for p in result['vehicle_handling']['fixture_bom'])
    result['drawings']=_drawings(result);result['geometry']=geometry_definition(result);result['manufacturing_schedule']=manufacturing_schedule(result)
    result['source_sha256']={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}
    if result['source_sha256']!=before:raise ValueError('structural study source changed during calculation; repeat under frozen inputs')
    # Final strict JSON roundtrip catches numpy scalars, NaN and incomplete API
    # values before a caller can publish a misleading partial calculation.
    return json.loads(encoded(result))


def _read_gzip(path,maximum=MAX_RAW):
    with gzip.open(path,'rb') as f:raw=f.read(maximum+1)
    if len(raw)>maximum:raise ValueError('bounded structural payload exceeded')
    return json.loads(raw)


def _gzip(value):return gzip.compress(encoded(value),mtime=0)


def _readme(value):
    b=value['civil']['beam_variants'][0];m=value['mechanical'];lines=[f'# Candidate-specific structural design study',f'',f'Exact candidate `{value["configuration_sha256"]}`; {value["controlled_aw3_kg"]:.3f} kg AW3 per car. All physical, engineering and manufacturing release flags remain false.',
        '',f'This package recalculates full force/moment equilibrium from the counted installed-mass placements. It does not scale the earlier26.4t interface result or adopt historic94ad dynamics.',
        '',f'Implemented results: hardpoint utilisation {m["hardpoint"]["worst"]["utilisation"]:.3f}; retained M8 segment-splice utilisation {m["collector_splice"]["utilisation"]:.3f}; two-spine-only dynamic bending stress {m["body_spine"]["combined_screen_pa"]/1e6:.1f} MPa. Failed controls remain recorded; deeper collector/spine alternatives require a new shared candidate identity and repeated mass/fit/dynamic checks.',
        '',f'Reference25m span: {b["concrete_volume_m3"]:.3f} m³ concrete, {b["reaction_rail_and_attachment_steel_mass_kg"]:.1f} kg new L-return/support steel, {b["reinforcement_mass_kg"]:.1f} kg reinforcement, {b["strand_mass_kg"]:.1f} kg strand, {b["gross_mass_kg"]:.1f} kg gross. This includes counted actual reaction rails, not the old7.51t allowance.',
        '',f'The original hypothetical60t@25m crane remains {"passing" if b["construction"]["crane"]["screen_pass"] else "rejected"}. A separately identifiedLTM1750 manufacturer chart is evaluated at its26m row,32.7m boom and204t ballast;2.6t hook and3t slings/spreader are counted. Actual crane configuration, wind, access, ground reactions/mats and lift plan remain unapproved.',
        '',f'Material interference witnesses: {value["interface_clearance"]["material_interference_count"]}. Zero witnesses alone does not qualify swept clearance or tolerances. New collector drilling is explicit machining with zero mass-removal credit. Concrete around fixed support embeds/blockouts is gross conservative stock, not completed net manufactured solids.',
        '',f'Soil cases50/100/150kPa and pile shaft/toe values are analyst sensitivities. No bearing resistance, groundwater, settlement or seismic acceptance is inferred from SoilGrids/open maps. Foundations and pier alternatives are separate, not additive.',
        '',f'[Section drawing](beam-section.svg) · [Geometry image](section.png) · [Candidate load plan](candidate-load-plan.svg) · [BOM](bom.json) · [Full study](study.json.gz) · [Applied-load export](load-envelope.json.gz) · [Counted geometry](geometry.json.gz)',
        '',f'Publication verification recomputes the structural study and independently checks retained payloads, exact source hashes, geometry-driven SVG and decoded section-image pixels. Image container bytes/fonts are not an engineering oracle.',
        '',f'QA and sequence records are unexecuted plans. No manufacturer quotation, concrete design code compliance, physical trial or site-specific design acceptance is claimed.']
    lines+=['','Primary references:']+[f'- [{r["id"]}]({r["url"]}) — {r["scope"]}' for r in value['assumptions']['references']]
    lines+=['',f'- [LTM1750-9.1 manufacturer technical data]({value["assumptions"]["larger_crane_reference"]["url"]}), printed pages8/26, accessed2026-10-23.']
    return '\n'.join(lines)+'\n'


def publish(output=OUTPUT,candidate=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);value=study(candidate)
    for name,payload in [('study.json.gz',value),('load-envelope.json.gz',value['load_export']),('geometry.json.gz',value['geometry'])]:(output/name).write_bytes(_gzip(payload))
    (output/'bom.json').write_bytes(encoded(value['bom'])+b'\n')
    for name,svg in value['drawings'].items():(output/name).write_text(svg)
    (output/'overview.svg').write_text(value['drawings']['beam-section.svg']);_image(value).save(output/'section.png');(output/'README.md').write_text(_readme(value))
    manifest=dict(schema=SCHEMA,configuration_sha256=value['configuration_sha256'],source_sha256=value['source_sha256'],files_sha256={name:sha256((output/name).read_bytes()).hexdigest() for name in sorted(FILES)},**FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest)+b'\n');return manifest


def _verified_payload(output=OUTPUT):
    from PIL import Image
    output=Path(output);manifest=json.loads((output/'manifest.json').read_text())
    if manifest['schema']!=SCHEMA or set(manifest['files_sha256'])!=FILES or any(manifest.get(k) is not False for k in FLAGS):raise ValueError('bounded unreleased structural manifest required')
    if any((output/name).is_symlink() or (output/name).stat().st_size>MAX_RAW for name in FILES):raise ValueError('owned regular bounded structural files required')
    for name,expected in manifest['files_sha256'].items():
        if sha256((output/name).read_bytes()).hexdigest()!=expected:raise ValueError('structural evidence hash differs')
    value=study()
    if manifest['source_sha256']!=value['source_sha256'] or manifest['configuration_sha256']!=value['configuration_sha256']:raise ValueError('structural source/candidate stale')
    if encoded(_read_gzip(output/'study.json.gz'))!=encoded(value):raise ValueError('structural study differs from independently recomputed quantities')
    for name,expected in [('load-envelope.json.gz',value['load_export']),('geometry.json.gz',value['geometry'])]:
        if encoded(_read_gzip(output/name))!=encoded(expected):raise ValueError('structural raw export differs')
    if encoded(json.loads((output/'bom.json').read_text()))!=encoded(value['bom']):raise ValueError('structural BOM differs')
    for name,text in {**value['drawings'],'overview.svg':value['drawings']['beam-section.svg'],'README.md':_readme(value)}.items():
        if (output/name).read_text()!=text:raise ValueError('structural presentation differs')
    with Image.open(output/'section.png') as im:
        if im.size!=(1000,600) or im.format!='PNG':raise ValueError('bounded structural image dimensions required')
        im.load()
        if im.convert('RGB').tobytes()!=_image(value).tobytes():raise ValueError('structural section geometry pixels differ')
    return manifest,value


def verify(output=OUTPUT):return _verified_payload(output)[0]


def read_summary(output=OUTPUT):
    manifest,value=_verified_payload(output);beams=value['civil']['beam_variants'];m=value['mechanical']
    return dict(schema=SCHEMA,configuration_sha256=value['configuration_sha256'],controlled_aw3_kg=value['controlled_aw3_kg'],
        mass_properties={k:v for k,v in value['mass_properties']['laden'].items()},unlocated_equipment_mass_kg=value['mass_properties']['unlocated_retained_mass_kg'],
        hardpoint_utilisation=m['hardpoint']['worst']['utilisation'],collector_splice_utilisation=m['collector_splice']['utilisation'],body_spine_stress_pa=m['body_spine']['combined_screen_pa'],
        protection_screens=dict(capture_pass=value['protection_structures']['capture']['unsupported_drop_screen_pass'],braking_pass=value['protection_structures']['braking']['deceleration_screen_pass'],braking_thermal_pass=value['protection_structures']['braking']['thermal_screen_pass']),
        manufacturing_lifting_fixture_mass_kg=value['vehicle_handling']['fixture_mass_kg'],
        beam_variants=[dict(id=b['id'],gross_mass_kg=b['gross_mass_kg'],material_formwork_cost_usd=b['material_and_formwork_cost_usd'],prestress_state=b['prestress']['state'],
            original_crane_pass=b['construction']['crane']['screen_pass'],larger_crane_pass=b['construction']['larger_crane_alternative']['radius_capacity_screen_pass'],passed=b['passed_implemented_screens']) for b in beams],
        interface_material_witnesses=value['interface_clearance']['material_interference_count'],all_implemented_screens_pass=value['all_implemented_screens_pass'],
        figures=['overview.svg','beam-section.svg','candidate-load-plan.svg','section.png'],source_sha256=manifest['source_sha256'],**FLAGS)
