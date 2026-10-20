"""Connected actual-section 3D elastic carbody-frame research adapter.

Uses the registered spatial Timoshenko element. Every beam is an owned RHS
part, while explicit rigid joint-centroid offsets form an *unqualified* upper
stiffness assumption. Sheets, glazing, doors and services contribute mass only.
No railway structural, weld, fatigue or suspension acceptance is inferred.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
import math

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu

from engineering.twin_workflow import core
from engineering.design_consistency import contracts
from engineering.civil_exploration.spatial_structure import element_matrices, skew


def _line(part):
    rotation=np.asarray(part['placement']['rotation']);translation=np.asarray(part['placement']['translation_m'])
    length=part['manufacturing']['primitives'][0]['dimensions_m'][0]
    return translation-rotation[:,0]*length/2,translation+rotation[:,0]*length/2


def _closest(a,b):
    """Exact nearest points of current orthogonal/parallel axis-aligned members."""
    p,q=a;r,s=b;u=q-p;v=s-r;i=int(np.argmax(abs(u)));j=int(np.argmax(abs(v)))
    if np.count_nonzero(abs(u)>1e-9)!=1 or np.count_nonzero(abs(v)>1e-9)!=1:
        raise ValueError('current carbody topology adapter requires axis-aligned owned members')
    if i!=j:
        first=np.clip((r[i]-p[i])/u[i],0.,1.);second=np.clip((p[j]-r[j])/v[j],0.,1.)
    else:
        low=max(min(p[i],q[i]),min(r[i],s[i]));high=min(max(p[i],q[i]),max(r[i],s[i]))
        x=(low+high)/2 if low<=high else min(max((p[i]+q[i])/2,min(r[i],s[i])),max(r[i],s[i]))
        first=np.clip((x-p[i])/u[i],0.,1.);second=np.clip((p[i]+first*u[i]-r[i])/v[i],0.,1.)
    x=p+first*u;y=r+second*v
    return float(first),float(second),x,y,float(np.linalg.norm(x-y))


def _section(part,material):
    s=part['analysis']['section'];E=material['young_pa'];G=E/(2*(1+material['poisson']));A=s['area_m2'];t=s['wall_m']
    return dict(EA_n=E*A,EIy_nm2=E*s['iy_m4'],EIz_nm2=E*s['iz_m4'],GJ_nm2=G*s['j_torsion_m4'],
        GAy_n=G*2*s['width_m']*t,GAz_n=G*2*(s['height_m']-2*t)*t,
        mass_kg_m=s['mass_kg_m'],polar_mass_kg_m=s['density_kg_m3']*(s['iy_m4']+s['iz_m4']))


def topology(candidate,*,refinement=1):
    from . import carbody_assembly as assembly
    if refinement not in (1,2,4):raise ValueError('registered frame refinement required')
    contracts.validate(candidate['contract'])
    rhs={p['id']:p for p in candidate['contract']['parts'] if p['analysis'].get('section')}
    lines={k:_line(v) for k,v in rhs.items()};breaks={k:{0.,1.} for k in rhs};links=[]
    for joint in candidate['contract']['assembly_joints']:
        ids=joint['endpoints']
        # A sheet/door retention record must never make its frame endpoints
        # into a fictitious perfectly rigid cross-body connection.
        if len(ids)<2 or not set(ids)<=set(rhs):continue
        choices=[]
        for i,first in enumerate(ids):
            for second in ids[i+1:]:
                t,u,x,y,d=_closest(lines[first],lines[second]);choices.append((d,first,second,t,u,x,y))
        # Minimum tree joins a header/bow to BOTH posts/rails, rather than
        # connecting the posts directly across its compliant beam span.
        connected={ids[0]}
        while len(connected)<len(ids):
            eligible=[r for r in choices if (r[1] in connected)!=(r[2] in connected)]
            d,first,second,t,u,x,y=min(eligible,key=lambda r:(r[0],r[1],r[2]))
            if d>.30:raise ValueError('declared frame joint has an unexplained gap above0.30m: '+joint['id'])
            breaks[first].add(round(t,12));breaks[second].add(round(u,12))
            links.append(dict(joint_id=joint['id'],first_part=first,second_part=second,first_fraction=t,second_fraction=u,
                first_point_m=x.tolist(),second_point_m=y.tolist(),offset_m=(y-x).tolist(),offset_length_m=d,
                model='Unqualified six-DOF rigid welded-joint/centroid offset; no measured joint stiffness or resistance'))
            connected|={first,second}
    # Physical non-beam mass is transferred at the exact closest beam point.
    # Its eccentric gravity couple is preserved; no panel shell stiffness added.
    allocations=[]
    for p in candidate['contract']['parts']:
        if p['id'] in rhs:continue
        point=np.asarray(p['properties']['cg_m']);options=[]
        for identity,(a,b) in lines.items():
            f=float(np.clip(np.dot(point-a,b-a)/np.dot(b-a,b-a),0.,1.));target=a+f*(b-a)
            options.append((float(np.linalg.norm(target-point)),identity,f,target))
        d,identity,f,target=min(options,key=lambda r:(r[0],r[1]))
        breaks[identity].add(round(f,12))
        allocations.append(dict(part_id=p['id'],beam_part_id=identity,fraction=f,point_m=point.tolist(),
            beam_point_m=target.tolist(),offset_m=(point-target).tolist(),mass_kg=p['properties']['mass_kg'],
            assumption='Gravity/load transfer only, with eccentric couple; actual clip/bracket path remains unqualified'))
    # Four independent vertical support seats at actual reference bolster ends.
    # These are a provisional body fixture, not a selected bogie/suspension.
    supports=[]
    for x in candidate['metadata']['bogie_reference_positions_m']:
        candidates=[p for p in rhs.values() if p['id'].startswith('cross-') and abs(p['placement']['translation_m'][0]-x)<1e-9]
        if len(candidates)!=1:raise ValueError('actual reference bolster missing')
        p=candidates[0]
        for f in (0.,1.):
            point=lines[p['id']][0]+f*(lines[p['id']][1]-lines[p['id']][0])
            supports.append(dict(part_id=p['id'],fraction=f,point_m=point.tolist(),
                fixed_dofs=[2],scope='Ideal four-seat body fixture at bolster beam ends; suspension stiffness/roll and actual seat geometry unqualified'))
    supports[0]['fixed_dofs']+=[0,1];supports[2]['fixed_dofs']+=[1]
    nodes=[];keys={};lookup={}
    def node(point):
        key=tuple(round(float(v),10) for v in point)
        if key not in keys:keys[key]=len(nodes);nodes.append(list(key))
        return keys[key]
    elements=[]
    for identity,part in rhs.items():
        expanded=set(breaks[identity]);ordered=sorted(expanded)
        for left,right in zip(ordered,ordered[1:]):
            for i in range(1,refinement):expanded.add(left+(right-left)*i/refinement)
        ordered=sorted(expanded);a,b=lines[identity]
        for f in ordered:lookup[(identity,round(f,12))]=node(a+f*(b-a))
        for left,right in zip(ordered,ordered[1:]):
            if (right-left)*np.linalg.norm(b-a)<1e-7:continue
            first=lookup[(identity,round(left,12))];second=lookup[(identity,round(right,12))]
            elements.append(dict(part_id=identity,part_revision=part['revision'],nodes=[first,second],
                section=deepcopy(part['analysis']['section']),section_rotation=part['placement']['rotation'],properties=_section(part,candidate['contract']['materials'][part['material']])))
    def at(identity,f):return lookup[(identity,round(f,12))]
    for link in links:link['nodes']=[at(link['first_part'],link['first_fraction']),at(link['second_part'],link['second_fraction'])]
    for allocation in allocations:allocation['node']=at(allocation['beam_part_id'],allocation['fraction'])
    for support in supports:support['node']=at(support['part_id'],support['fraction'])
    parents=list(range(len(nodes)))
    def root(i):
        while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
        return i
    for link in links:
        a,b=[root(i) for i in link['nodes']]
        if a!=b:parents[b]=a
    roots=sorted({root(i) for i in range(len(nodes))});root_indices={r:i for i,r in enumerate(roots)}
    masters=[root_indices[root(i)] for i in range(len(nodes))];master_coordinates=[nodes[r] for r in roots]
    transforms=[]
    for i,master in enumerate(masters):
        B=np.eye(6);B[:3,3:]=-skew(np.asarray(nodes[i])-np.asarray(master_coordinates[master]));transforms.append(B)
    for support in supports:
        # A fixed translational seat on an offset slave needs linear constraints,
        # not simply fixing the master's translation. Current seats are masters
        # or identical-coordinate welded tie nodes, verified rather than assumed.
        i=support['node'];offset=np.asarray(nodes[i])-np.asarray(master_coordinates[masters[i]])
        if np.linalg.norm(offset)>1e-8:raise ValueError('fixture seat tied to offset master; explicit constraint adapter required')
    return dict(candidate_revision=candidate['revision'],refinement=refinement,nodes_m=nodes,elements=elements,
        rigid_links=links,load_allocations=allocations,supports=supports,masters=masters,
        master_coordinates_m=master_coordinates,transforms=transforms,
        stiffness_excluded=[p['id'] for p in candidate['contract']['parts'] if p['id'] not in rhs])


def _assemble(model):
    rows=[];cols=[];data=[];stored=[];masters=model['masters'];transforms=model['transforms']
    for element in model['elements']:
        a,b=element['nodes'];_,K,R,L=element_matrices(model['nodes_m'][a],model['nodes_m'][b],element['properties'])
        if not np.allclose(R@np.asarray(element['section_rotation']),np.eye(3),atol=1e-8):
            raise ValueError('actual RHS local axes differ from registered element section orientation')
        B=np.zeros((12,12));B[:6,:6]=transforms[a];B[6:,6:]=transforms[b]
        condensed=B.T@K@B;ix=[6*masters[a]+i for i in range(6)]+[6*masters[b]+i for i in range(6)]
        r,c=np.meshgrid(ix,ix,indexing='ij');rows.extend(r.ravel());cols.extend(c.ravel());data.extend(condensed.ravel())
        stored.append((element,K,R,L,ix,B))
    n=6*len(model['master_coordinates_m']);K=coo_matrix((data,(rows,cols)),shape=(n,n)).tocsc()
    fixed=sorted({6*masters[s['node']]+d for s in model['supports'] for d in s['fixed_dofs']})
    free=np.asarray([i for i in range(n) if i not in fixed]);solver=splu(K[free][:,free])
    return K,fixed,free,solver,stored


def solve(candidate,*,refinement=1,vertical_scale=1.,longitudinal_fraction=0.,lateral_fraction=0.,planning=True,left_share=.5):
    from . import contracts as configuration
    for value in (vertical_scale,longitudinal_fraction,lateral_fraction,left_share):
        if type(value) not in (int,float) or not math.isfinite(value):raise ValueError('finite frame load required')
    if vertical_scale<=0 or not 0<=left_share<=1 or max(abs(longitudinal_fraction),abs(lateral_fraction))>.5:
        raise ValueError('load sensitivity outside bounded research domain')
    model=topology(candidate,refinement=refinement);K,fixed,free,solver,stored=_assemble(model)
    F=np.zeros(K.shape[0]);load_records=[];nodes=model['nodes_m'];masters=model['masters'];B=model['transforms']
    acceleration=9.80665*np.asarray([longitudinal_fraction,lateral_fraction,-vertical_scale])
    def load(n,mass,point=None,kind='represented-self-weight'):
        point=np.asarray(nodes[n] if point is None else point);force=mass*acceleration
        moment=np.cross(point-np.asarray(nodes[n]),force);wrench=np.r_[force,moment]
        master=masters[n];F[master*6:master*6+6]+=B[n].T@wrench
        load_records.append(dict(node=n,mass_kg=mass,point_m=point.tolist(),force_n=force.tolist(),kind=kind))
    for element,_,_,length,_,_ in stored:
        a,b=element['nodes'];mass=element['properties']['mass_kg_m']*length
        load(a,mass/2);load(b,mass/2)
    for allocation in model['load_allocations']:load(allocation['node'],allocation['mass_kg'],allocation['point_m'])
    represented=sum(r['mass_kg'] for r in load_records);prototype=configuration.prototype_configuration();v=prototype['values'];cars=v['car_count']['value']
    planning_mass=v['tare_mass']['value']/cars+v['crush_passengers']['value']/cars*75.
    additional=planning_mass-represented if planning else 0.
    if additional<0:raise ValueError('represented shell exceeds planning mass; reconciliation required')
    # Unallocated planning mass is a sensitivity at floor height; no guessed
    # component or axle map, removal credit or adoption of the planning tare.
    if additional:
        for sign,share in ((-1,1-left_share),(1,left_share)):
            ids=[p for p in candidate['contract']['parts'] if p['id'] in candidate['metadata']['primary_sill_ids'] and p['placement']['translation_m'][1]*sign>0]
            relevant=[(e,L) for e,_,_,L,_,_ in stored if e['part_id'] in {p['id'] for p in ids}]
            total_length=sum(L for _,L in relevant)
            for e,L in relevant:
                for n in e['nodes']:
                    point=list(nodes[n]);point[2]=candidate['metadata']['dimensions_m']['floor_above_rail']
                    load(n,additional*share*L/(2*total_length),point,'unallocated-planning-tare-and-crush-floor-sensitivity')
    u=np.zeros(len(F));u[free]=solver.solve(F[free]);reaction=K@u-F
    free_residual=float(np.linalg.norm(reaction[free])/max(np.linalg.norm(F),1.))
    displacements=[]
    for i in range(len(nodes)):displacements.append((B[i]@u[6*masters[i]:6*masters[i]+6]).tolist())
    forces=[]
    for element,Kg,R,L,ix,transform in stored:
        dofs=transform@u[ix];world=Kg@dofs;local=np.concatenate([R@world[i:i+3] for i in range(0,12,3)])
        s=element['section'];stress=max(abs(local[0]),abs(local[6]))/s['area_m2']+max(abs(local[4]),abs(local[10]))*s['height_m']/2/s['iy_m4']+max(abs(local[5]),abs(local[11]))*s['width_m']/2/s['iz_m4']
        forces.append(dict(part_id=element['part_id'],nodes=element['nodes'],local_end_forces_n_nm=local.tolist(),gross_elastic_fibre_stress_pa=float(stress)))
    applied_force=sum((np.asarray(r['force_n']) for r in load_records),np.zeros(3));applied_moment=sum((np.cross(r['point_m'],r['force_n']) for r in load_records),np.zeros(3))
    support_records=[];support_force=np.zeros(3);support_moment=np.zeros(3)
    for master,point in enumerate(model['master_coordinates_m']):
        force=reaction[6*master:6*master+3];moment=reaction[6*master+3:6*master+6]
        support_force+=force;support_moment+=moment+np.cross(point,force)
    for support in model['supports']:
        master=masters[support['node']];support_records.append(dict(point_m=support['point_m'],fixed_dofs=support['fixed_dofs'],reaction_n_nm=reaction[6*master:6*master+6].tolist()))
    return dict(schema='osr-carbody-space-frame/1',candidate_revision=candidate['revision'],prototype_revision=prototype['revision'],refinement=refinement,
        input=dict(vertical_scale=vertical_scale,longitudinal_fraction=longitudinal_fraction,lateral_fraction=lateral_fraction,planning=planning,left_share=left_share,
            planning_tare_per_car_kg=v['tare_mass']['value']/cars,planning_crush_passengers_per_car=v['crush_passengers']['value']/cars,synthetic_passenger_mass_kg=75.),
        represented_mass_kg=represented,applied_mass_kg=sum(r['mass_kg'] for r in load_records),additional_unallocated_planning_mass_kg=additional,
        nodes_m=nodes,node_displacements_m_rad=displacements,elements=[{k:v for k,v in e.items() if k!='properties'} for e in model['elements']],
        rigid_joint_offsets=model['rigid_links'],mass_only_allocations=model['load_allocations'],stiffness_excluded_part_ids=model['stiffness_excluded'],
        supports=support_records,member_forces=forces,
        maximum_vertical_displacement_m=max(abs(d[2]) for d in displacements),maximum_lateral_displacement_m=max(abs(d[1]) for d in displacements),
        maximum_longitudinal_displacement_m=max(abs(d[0]) for d in displacements),maximum_rotation_rad=max(max(abs(v) for v in d[3:]) for d in displacements),
        maximum_gross_elastic_fibre_stress_pa=max(r['gross_elastic_fibre_stress_pa'] for r in forces),
        free_equation_residual_relative=free_residual,applied_force_n=applied_force.tolist(),support_force_n=support_force.tolist(),
        force_balance_relative=float(np.linalg.norm(applied_force+support_force)/max(np.linalg.norm(applied_force),1.)),
        applied_moment_nm=applied_moment.tolist(),support_moment_nm=support_moment.tolist(),
        moment_balance_relative=float(np.linalg.norm(applied_moment+support_moment)/max(sum(np.linalg.norm(r['force_n'])*max(np.linalg.norm(r['point_m']),1.) for r in load_records),1.)),
        adopted_stress_allowable_pa=None,adopted_deflection_limit_m=None,physical_validation=False,manufacturing_release=False,
        scope='Linear actual-RHS3Dframe with rigid welded-joint offsets and ideal4seat fixture; stiffness/loads/constraints are hypotheses, not adopted railway evidence')


def benchmarks():
    """Independent analytical Timoshenko cantilever/axial/torsion controls."""
    p=dict(EA_n=210e9*.08,EIy_nm2=210e9*.0006,EIz_nm2=210e9*.0012,GJ_nm2=80e9*.0008,
        GAy_n=80e9*.06,GAz_n=80e9*.05,mass_kg_m=628.,polar_mass_kg_m=4.)
    length=4.;_,K,_,_=element_matrices([0,0,0],[length,0,0],p)
    F=np.asarray([500.,1000.,2000.,300.,0.,0.]);u=np.linalg.solve(K[6:,6:],F)
    exact=np.asarray([F[0]*length/p['EA_n'],F[1]*(length**3/(3*p['EIz_nm2'])+length/p['GAy_n']),
        F[2]*(length**3/(3*p['EIy_nm2'])+length/p['GAz_n']),F[3]*length/p['GJ_nm2'],
        -F[2]*length**2/(2*p['EIy_nm2']),F[1]*length**2/(2*p['EIz_nm2'])])
    relative=float(np.max(abs(u-exact))/max(np.max(abs(exact)),1e-12))
    return dict(schema='osr-carbody-frame-controls/1',cantilever_relative_error=relative,
        passed=relative<1e-9,scope='Independent axial/two-axis Timoshenko bending/torsion closed forms, no railway capacity acceptance')


def _report_uncached(candidate):
    from . import baseline, contracts as configuration
    if candidate['metadata']['prototype_revision']!=configuration.prototype_configuration()['revision']:
        raise ValueError('stale prototype revision for frame analysis')
    coarse=solve(candidate,refinement=1);fine=solve(candidate,refinement=2)
    adverse=solve(candidate,refinement=2,vertical_scale=2.)
    lateral=solve(candidate,refinement=2,lateral_fraction=.1)
    brake=solve(candidate,refinement=2,longitudinal_fraction=.2)
    eccentric=solve(candidate,refinement=2,left_share=.8)
    own=solve(candidate,refinement=2,planning=False)
    cases=dict(planning=coarse,refined_planning=fine,double_vertical=adverse,lateral_sensitivity=lateral,
        braking_sensitivity=brake,eccentric_floor_sensitivity=eccentric,represented_self_weight=own)
    refinement=abs(fine['maximum_vertical_displacement_m']/coarse['maximum_vertical_displacement_m']-1)
    reference=next(r for r in core.read(baseline.DATA)['facts'] if r['id']=='steel.yield_by_thickness')
    wall=candidate['variables']['frame_wall_m']
    bands=sorted(reference['value']);nominal_yield=next(value for maximum,value in bands if wall<=maximum)
    # A transparent, nonapproved study target makes the small/slender designs
    # fail visibly. Passing does not adopt a rail deflection limit or design
    # resistance; material/joint/suspension validation remains mandatory.
    deflection_target=candidate['metadata']['dimensions_m']['length']/1000
    checks=dict(independent_element_controls=benchmarks()['passed'],mesh_refinement_diagnostic=refinement<.05,
        provisional_nominal_S355_elastic_guardrail=max(r['maximum_gross_elastic_fibre_stress_pa'] for r in cases.values())<=nominal_yield,
        provisional_length_over_1000_vertical_target=max(r['maximum_vertical_displacement_m'] for r in cases.values())<=deflection_target,
        mass_reconstruction=math.isclose(own['applied_mass_kg'],contracts.summary(candidate['contract'])['mass_kg'],rel_tol=1e-9),
        adverse_double_load_control=math.isclose(adverse['maximum_vertical_displacement_m'],2*fine['maximum_vertical_displacement_m'],rel_tol=1e-8),
        all_equilibrium=all(max(r['force_balance_relative'],r['moment_balance_relative'],r['free_equation_residual_relative'])<1e-7 for r in cases.values()))
    checks.update({k:None for k in ('joint-stiffness-and-resistance','shell-local-buckling-and-panel-mounts','railway-load-adoption-and-fatigue',
        'actual-bogie-suspension-and-equipment-maps','nonlinear-imperfections-and-physical-correlation')})
    result=dict(schema='osr-carbody-connected-frame-study/1',candidate_revision=candidate['revision'],part_revisions={p['id']:p['revision'] for p in candidate['contract']['parts']},
        checks=checks,failed_checks=[k for k,v in checks.items() if v is False],held_checks=[k for k,v in checks.items() if v is None],
        state='failed' if any(v is False for v in checks.values()) else 'hold',cases=cases,benchmarks=benchmarks(),
        refinement_relative_change=refinement,numerical_refinement_tolerance=.05,
        provisional_targets=dict(nominal_yield_pa=nominal_yield,yield_reference_fact=deepcopy(reference),
            peak_vertical_displacement_m=deflection_target,deflection_basis='Unapproved comparison target L/1000 chosen for this frame stiffening study; no normative railway or suspension/clearance criterion',
            load_sensitivity_basis='Repository tare/crush plus synthetic75kg/passenger;2xvertical,0.1glateral,0.2glongitudinal and80/20floor sensitivity are not adopted railway loads',approved=False),
        joint_model='Exact member centrelines and nearest joint projections; centroid eccentricities retained as rigid sixDOF offsets, ideal unqualified welding',
        support_model='Four translational bodyfixture seats at real reference bolster endpoints; actual bogie/suspension/roll stiffness unadopted',
        omissions=['No stiffness from glazing/cladding/floor sheets','No weld stress/local plate/shell buckling','No calibrated joint, local floor or suspension stiffness',
            'Planning tare includes unreconciled complete vehicle mass; uniformly allocated extra load is only a gross sensitivity',
            'Thin-wall Bredt RHS torsion and wall-area Timoshenko shear; no calibrated radii/warping/local stress',
            'Small-displacement elastic material; geometric/material nonlinearity and adopted resistance limits unresolved'],
        digital_specification_complete=False,**core.FLAGS)
    result['revision']=core.digest(result);return result


def _source_signature():
    from . import baseline, contracts as configuration
    names=[Path(__file__),core.ROOT/'engineering/civil_exploration/spatial_structure.py',
        core.ROOT/'engineering/civil_exploration/train_bridge.py',baseline.DATA]
    return tuple(core.sha(path) for path in names)+(core.digest(configuration.prototype_configuration()),)


@lru_cache(maxsize=8)
def _cached_report(candidate_bytes,source_signature):
    if source_signature!=_source_signature():raise ValueError('frame source changed before analysis')
    result=_report_uncached(json.loads(candidate_bytes))
    if source_signature!=_source_signature():raise ValueError('frame source changed during analysis')
    return result


def report(candidate):
    """Bounded immutable-value cache; full geometry, source and loads key it.

    Candidate IDs/revisions alone cannot reuse a result. A deep copy prevents
    callers mutating one assessment from modifying another cached report.
    """
    return deepcopy(_cached_report(core.encoded(candidate),_source_signature()))


def plot(result,path):
    """Reproducible actual frame mesh and exaggerated displacement diagnostic."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    r=result['cases']['refined_planning'];nodes=np.asarray(r['nodes_m']);u=np.asarray(r['node_displacements_m_rad'])
    scale=min(100.,.35/max(r['maximum_vertical_displacement_m'],1e-12))
    fig,axes=plt.subplots(2,1,figsize=(12,6),layout='constrained')
    for e in r['elements']:
        a,b=e['nodes'];points=nodes[[a,b]];shifted=points+u[[a,b],:3]*scale
        if abs(points[:,1].mean())>.5:
            axes[0].plot(points[:,0],points[:,2],color='#8aa1b0',alpha=.4,lw=.5)
            axes[0].plot(shifted[:,0],shifted[:,2],color='#196185',lw=.7)
    for link in r['rigid_joint_offsets']:
        a,b=np.asarray(link['first_point_m']),np.asarray(link['second_point_m'])
        if abs((a[1]+b[1])/2)>.5:axes[0].plot([a[0],b[0]],[a[2],b[2]],color='#d48631',ls='--',lw=.6)
    axes[0].set(xlabel='Car longitudinal x /m',ylabel='Rail datum z /m',title=f'Owned RHS frame; deformation ×{scale:.1f} (ideal rigid joints/fixture; unqualified)')
    axes[0].axis('equal');axes[1].scatter(nodes[:,0],u[:,2]*1000,s=8,c=nodes[:,1],cmap='coolwarm')
    axes[1].set(xlabel='Car longitudinal x /m',ylabel='Vertical displacement /mm',title='Gross planning tare + synthetic crush load; no adopted structural acceptance')
    fig.savefig(path,dpi=120);plt.close(fig)
