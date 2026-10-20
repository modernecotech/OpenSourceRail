"""Finite six-DOF connection hypotheses on the owned carbody RHS frame.

Section/member-derived stiffness scales are deliberately hypothetical. They are
not weld, bracket or measured joint stiffnesses. No passing assumption supplies
missing connection qualification or independently accepts the vehicle design.
"""
from copy import deepcopy
from functools import lru_cache
import json
import math
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu

from engineering.twin_workflow import core
from engineering.civil_exploration.spatial_structure import element_matrices,skew
from . import carbody_frame as frame
from . import contracts as configuration

FACTORS=(.1,1.,100000.)
CASES=('refined_planning','double_vertical','lateral_sensitivity','braking_sensitivity','eccentric_floor_sensitivity','represented_self_weight')


def rigid_arm(offset):
    B=np.eye(6);B[:3,3:]=-skew(np.asarray(offset,dtype=float));return B


def reference_compliance(part,material):
    """Dimensional beam-compliance yardstick, not a connection constitutive law."""
    s=part['analysis']['section'];length=frame._line(part);L=float(np.linalg.norm(length[1]-length[0]))
    p=frame._section(part,material)
    local=np.diag([L/p['EA_n'],L**3/(12*p['EIz_nm2'])+L/p['GAy_n'],
        L**3/(12*p['EIy_nm2'])+L/p['GAz_n'],L/p['GJ_nm2'],L/p['EIy_nm2'],L/p['EIz_nm2']])
    R=np.asarray(part['placement']['rotation']).T;T=np.zeros((6,6));T[:3,:3]=R;T[3:,3:]=R
    return T.T@local@T,dict(part_id=part['id'],part_revision=part['revision'],characteristic_length_m=L,
        section=deepcopy(s),local_reference_compliance_diagonal=local.diagonal().tolist(),
        basis='EA/L,12EI/L^3 plus wall-area shear, GJ/L and EI/L dimensional yardsticks; no tested weld/joint law')


def model(candidate):
    """Recover independent physical-part nodes, including coincident butt ends."""
    topology=frame.topology(candidate,refinement=2);parts={p['id']:p for p in candidate['contract']['parts']}
    identities={};nodes=[];owned=[]
    def node(part_id,old):
        key=(part_id,old)
        if key not in identities:
            identities[key]=len(nodes);nodes.append(topology['nodes_m'][old]);owned.append(dict(part_id=part_id,rigid_model_node=old))
        return identities[key]
    elements=[]
    for source in topology['elements']:
        e=deepcopy(source);e['nodes']=[node(e['part_id'],i) for i in source['nodes']];elements.append(e)
    links=[]
    for source in topology['rigid_links']:
        a=node(source['first_part'],source['nodes'][0]);b=node(source['second_part'],source['nodes'][1])
        if a==b:raise ValueError('distinct physical parts were merged across a finite connector')
        point=(np.asarray(nodes[a])+nodes[b])/2
        A=rigid_arm(point-nodes[a]);B=rigid_arm(point-nodes[b]);C=[];definitions=[]
        for identity in (source['first_part'],source['second_part']):
            p=parts[identity];compliance,definition=reference_compliance(p,candidate['contract']['materials'][p['material']])
            C.append(compliance);definitions.append(definition)
        base=np.linalg.inv(C[0]+C[1])
        if np.min(np.linalg.eigvalsh(base))<=0:raise ValueError('positive definite finite connector required')
        links.append(dict(source=deepcopy(source),nodes=[a,b],point_m=point.tolist(),first_arm=A,second_arm=B,
            reference_stiffness=base,reference_definitions=definitions))
    supports=[dict(**s,finite_node=node(s['part_id'],s['node'])) for s in topology['supports']]
    allocations=[dict(**a,finite_node=node(a['beam_part_id'],a['node'])) for a in topology['load_allocations']]
    return dict(nodes_m=nodes,node_ownership=owned,elements=elements,connectors=links,supports=supports,
        mass_only_allocations=allocations,stiffness_excluded=topology['stiffness_excluded'])


def _beam_blocks(system):
    rows=[];cols=[];values=[];stored=[]
    for e in system['elements']:
        a,b=e['nodes'];_,K,R,L=element_matrices(system['nodes_m'][a],system['nodes_m'][b],e['properties'])
        if not np.allclose(R@np.asarray(e['section_rotation']),np.eye(3),atol=1e-8):raise ValueError('unmatched actual beam section axes')
        ix=[6*a+i for i in range(6)]+[6*b+i for i in range(6)]
        r,c=np.meshgrid(ix,ix,indexing='ij');rows.extend(r.ravel());cols.extend(c.ravel());values.extend(K.ravel())
        stored.append((e,K,R,L,ix))
    n=6*len(system['nodes_m'])
    return coo_matrix((values,(rows,cols)),shape=(n,n)).tocsc(),stored


def _connector_matrix(system,factor):
    if type(factor) not in (int,float) or not math.isfinite(factor) or factor<=0:raise ValueError('positive finite stiffness factor required')
    rows=[];cols=[];values=[]
    for connector in system['connectors']:
        a,b=connector['nodes'];D=np.hstack([-connector['first_arm'],connector['second_arm']])
        K=D.T@(connector['reference_stiffness']*factor)@D
        ix=[6*a+i for i in range(6)]+[6*b+i for i in range(6)]
        r,c=np.meshgrid(ix,ix,indexing='ij');rows.extend(r.ravel());cols.extend(c.ravel());values.extend(K.ravel())
    n=6*len(system['nodes_m'])
    return coo_matrix((values,(rows,cols)),shape=(n,n)).tocsc()


def loads(candidate,system,stored,case):
    """Same actual mass, gross reference allocation and eccentric load points."""
    inp=case['input'];acc=9.80665*np.asarray([inp['longitudinal_fraction'],inp['lateral_fraction'],-inp['vertical_scale']])
    F=np.zeros(6*len(system['nodes_m']));records=[]
    def add(n,mass,point=None,kind='represented-self-weight'):
        point=np.asarray(system['nodes_m'][n] if point is None else point);force=mass*acc
        F[6*n:6*n+6]+=np.r_[force,np.cross(point-system['nodes_m'][n],force)]
        records.append(dict(node=n,mass_kg=mass,point_m=point.tolist(),force_n=force.tolist(),kind=kind))
    for e,_,_,L,_ in stored:
        mass=e['properties']['mass_kg_m']*L
        for n in e['nodes']:add(n,mass/2)
    for a in system['mass_only_allocations']:add(a['finite_node'],a['mass_kg'],a['point_m'])
    represented=sum(r['mass_kg'] for r in records)
    target=inp['planning_tare_per_car_kg']+inp['planning_crush_passengers_per_car']*inp['synthetic_passenger_mass_kg']
    additional=target-represented if inp['planning'] else 0.
    if additional<0:raise ValueError('finite frame mass exceeds unreconciled planning reference')
    if additional:
        byid={p['id']:p for p in candidate['contract']['parts']}
        for sign,share in ((-1,1-inp['left_share']),(1,inp['left_share'])):
            ids={identity for identity in candidate['metadata']['primary_sill_ids'] if byid[identity]['placement']['translation_m'][1]*sign>0}
            selected=[(e,L) for e,_,_,L,_ in stored if e['part_id'] in ids];total=sum(L for _,L in selected)
            for e,L in selected:
                for n in e['nodes']:
                    point=list(system['nodes_m'][n]);point[2]=candidate['metadata']['dimensions_m']['floor_above_rail']
                    add(n,additional*share*L/(2*total),point,'unallocated-planning-tare-and-crush-floor-sensitivity')
    actual=sum(r['mass_kg'] for r in records)
    if not math.isclose(actual,case['applied_mass_kg'],rel_tol=1e-10):raise ValueError('finite and rigid frame load allocations differ')
    force=sum((np.asarray(r['force_n']) for r in records),np.zeros(3))
    moment=sum((np.cross(r['point_m'],r['force_n']) for r in records),np.zeros(3))
    if not np.allclose(force,case['applied_force_n'],rtol=1e-10,atol=1e-5) or not np.allclose(moment,case['applied_moment_nm'],rtol=1e-10,atol=1e-5):
        raise ValueError('finite and rigid frame load wrenches differ')
    return F,dict(applied_mass_kg=actual,represented_mass_kg=represented,additional_unallocated_mass_kg=additional,
        applied_force_n=force.tolist(),applied_moment_nm=moment.tolist(),load_records_sha256=core.digest(records),
        moment_normalisation_nm=sum(np.linalg.norm(r['force_n'])*max(np.linalg.norm(r['point_m']),1.) for r in records))


def _response(system,stored,K,u,F,load,factor,reference,targets,fixed):
    reactions=K@u-F;free=np.asarray([i for i in range(len(u)) if i not in fixed]);d=u.reshape(-1,6)
    support_force=np.sum(reactions.reshape(-1,6)[:,:3],axis=0)
    support_moment=np.sum(reactions.reshape(-1,6)[:,3:],axis=0)+sum((np.cross(point,reactions[6*i:6*i+3]) for i,point in enumerate(system['nodes_m'])),np.zeros(3))
    joint_rows=[]
    for i,c in enumerate(system['connectors']):
        a,b=c['nodes'];relative=c['second_arm']@d[b]-c['first_arm']@d[a]
        resultant=c['reference_stiffness']*factor@relative
        first=-c['first_arm'].T@resultant;second=c['second_arm'].T@resultant
        arm_balance=np.r_[first[:3]+second[:3],first[3:]+second[3:]+np.cross(np.asarray(system['nodes_m'][a])-c['point_m'],first[:3])+np.cross(np.asarray(system['nodes_m'][b])-c['point_m'],second[:3])]
        joint_rows.append(dict(connector=i,joint_id=c['source']['joint_id'],first_part=c['source']['first_part'],second_part=c['source']['second_part'],
            relative_at_joint_m_rad=relative.tolist(),resultant_on_second_at_joint_n_nm=resultant.tolist(),
            first_node_wrench_n_nm=first.tolist(),second_node_wrench_n_nm=second.tolist(),
            action_reaction_force_relative=float(np.linalg.norm(arm_balance[:3])/max(np.linalg.norm(resultant[:3]),1.)),
            action_reaction_moment_relative=float(np.linalg.norm(arm_balance[3:])/max(np.linalg.norm(resultant[3:])+np.linalg.norm(resultant[:3])*(np.linalg.norm(np.asarray(system['nodes_m'][a])-c['point_m'])+np.linalg.norm(np.asarray(system['nodes_m'][b])-c['point_m'])),1.))))
    members={}
    for e,Ke,R,L,ix in stored:
        world=Ke@u[ix];local=np.concatenate([R@world[i:i+3] for i in range(0,12,3)]);s=e['section']
        stress=max(abs(local[0]),abs(local[6]))/s['area_m2']+max(abs(local[4]),abs(local[10]))*s['height_m']/2/s['iy_m4']+max(abs(local[5]),abs(local[11]))*s['width_m']/2/s['iz_m4']
        if e['part_id'] not in members or stress>members[e['part_id']]['gross_elastic_fibre_stress_pa']:
            members[e['part_id']]=dict(part_id=e['part_id'],part_revision=e['part_revision'],critical_segment_nodes=e['nodes'],
                gross_elastic_fibre_stress_pa=float(stress),simultaneous_local_end_forces_n_nm=local.tolist())
    vertical=float(np.max(abs(d[:,2])));stress=max(r['gross_elastic_fibre_stress_pa'] for r in members.values())
    matched=np.asarray([reference['node_displacements_m_rad'][r['rigid_model_node']] for r in system['node_ownership']])
    translation_difference=float(np.max(abs(d[:,:3]-matched[:,:3])));rotation_difference=float(np.max(abs(d[:,3:]-matched[:,3:])))
    translation_relative=translation_difference/max(float(np.max(abs(matched[:,:3]))),1e-12)
    rotation_relative=rotation_difference/max(float(np.max(abs(matched[:,3:]))),1e-12)
    force_error=float(np.linalg.norm(support_force+load['applied_force_n'])/max(np.linalg.norm(load['applied_force_n']),1.))
    moment_error=float(np.linalg.norm(support_moment+load['applied_moment_nm'])/max(load['moment_normalisation_nm'],1.))
    equation_error=float(np.linalg.norm(reactions[free])/max(np.linalg.norm(F),1.))
    return dict(input=deepcopy(reference['input']),load=load,maximum_vertical_displacement_m=vertical,
        maximum_rotation_rad=float(np.max(abs(d[:,3:]))),maximum_gross_elastic_fibre_stress_pa=stress,
        maximum_joint_translation_m=max(float(np.linalg.norm(r['relative_at_joint_m_rad'][:3])) for r in joint_rows),
        maximum_joint_rotation_rad=max(float(np.linalg.norm(r['relative_at_joint_m_rad'][3:])) for r in joint_rows),
        maximum_translation_difference_from_rigid_m=translation_difference,maximum_rotation_difference_from_rigid_rad=rotation_difference,
        translation_difference_from_rigid_relative=translation_relative,rotation_difference_from_rigid_relative=rotation_relative,
        nodewise_difference_from_rigid_relative=max(translation_relative,rotation_relative),
        force_balance_relative=force_error,moment_balance_relative=moment_error,free_equation_residual_relative=equation_error,
        support_force_n=support_force.tolist(),support_moment_nm=support_moment.tolist(),
        support_reactions=[dict(point_m=s['point_m'],fixed_dofs=s['fixed_dofs'],reaction_n_nm=reactions[6*s['finite_node']:6*s['finite_node']+6].tolist()) for s in system['supports']],
        joints=joint_rows,member_critical_segments=list(members.values()),
        research_checks=dict(provisional_nominal_S355_elastic_guardrail=stress<=targets['nominal_yield_pa'],
            provisional_length_over_1000_vertical_target=vertical<=targets['peak_vertical_displacement_m']),
        actual_joint_stiffness_known=False,actual_connection_capacity_verified=False,
        linear_model_validity='unestablished; metre-scale outputs are outside credible small-deformation interpretation' if vertical>=1. else 'unestablished; linear numerical sensitivity only',**core.FLAGS)


def benchmarks():
    """Coincident nodes stay distinct; compliant root/beam has an exact control."""
    p=dict(EA_n=210e9*.08,EIy_nm2=210e9*.0006,EIz_nm2=210e9*.0012,GJ_nm2=80e9*.0008,
        GAy_n=80e9*.06,GAz_n=80e9*.05,mass_kg_m=628.,polar_mass_kg_m=4.)
    L=4.;_,beam,_,_=element_matrices([0,0,0],[L,0,0],p);spring=np.diag([1e8,2e7,3e7,4e6,5e6,6e6])
    K=beam.copy();K[:6,:6]+=spring;force=np.asarray([500.,1000.,2000.,300.,80.,120.]);F=np.r_[np.zeros(6),force]
    displacement=np.linalg.solve(K,F)
    root_wrench=np.r_[force[:3],force[3:]+np.cross([L,0,0],force[:3])];root=np.linalg.solve(spring,root_wrench)
    # Independent Timoshenko cantilever including imposed tip moments.
    fixed=np.asarray([force[0]*L/p['EA_n'],force[1]*(L**3/(3*p['EIz_nm2'])+L/p['GAy_n'])+force[5]*L**2/(2*p['EIz_nm2']),
        force[2]*(L**3/(3*p['EIy_nm2'])+L/p['GAz_n'])-force[4]*L**2/(2*p['EIy_nm2']),force[3]*L/p['GJ_nm2'],
        -force[2]*L**2/(2*p['EIy_nm2'])+force[4]*L/p['EIy_nm2'],force[1]*L**2/(2*p['EIz_nm2'])+force[5]*L/p['EIz_nm2']])
    expected=fixed+rigid_arm([L,0,0])@root
    relative=float(np.max(abs(displacement[6:]-expected))/max(np.max(abs(expected)),1e-12))
    # Two separate six-DOF nodes at exactly the same coordinate: ground/spring.
    D=np.hstack([-np.eye(6),np.eye(6)]);matrix=D.T@spring@D
    moved=np.linalg.solve(matrix[6:,6:],force)
    coincident_error=float(np.max(abs(moved-force/spring.diagonal()))/max(np.max(abs(moved)),1e-12))
    a=np.asarray([.2,-.3,.4]);b=np.asarray([-.1,.5,.7]);point=(a+b)/2
    theta=np.asarray([.01,-.02,.03]);translation=np.asarray([.12,.13,-.4])
    first=np.r_[translation+np.cross(theta,a),theta];second=np.r_[translation+np.cross(theta,b),theta]
    delta=rigid_arm(point-b)@second-rigid_arm(point-a)@first
    rigid_motion=float(np.max(abs(delta)))
    return dict(beam_on_finite_spring_relative_error=relative,separate_coincident_node_spring_relative_error=coincident_error,
        eccentric_rigid_body_motion_relative_components_m_rad=delta.tolist(),
        passed=max(relative,coincident_error)<1e-9 and rigid_motion<1e-14,scope='Independent6DOFspring and beam/compliantroot controls; hypothetical stiffness only')


def _sources():
    paths=[Path(__file__),Path(frame.__file__),core.ROOT/'engineering/civil_exploration/spatial_structure.py',core.ROOT/'engineering/civil_exploration/train_bridge.py']
    return {p.relative_to(core.ROOT).as_posix():core.sha(p) for p in paths}


def _run(candidate,rigid):
    before=_sources();system=model(candidate);beam,stored=_beam_blocks(system)
    fixed=sorted({6*s['finite_node']+i for s in system['supports'] for i in s['fixed_dofs']});free=np.asarray([i for i in range(beam.shape[0]) if i not in fixed])
    loads_bycase={key:loads(candidate,system,stored,rigid['cases'][key]) for key in CASES}
    Fs=np.column_stack([loads_bycase[key][0] for key in CASES]);variants=[]
    for factor in FACTORS:
        K=beam+_connector_matrix(system,factor);solver=splu(K[free][:,free]);U=np.zeros_like(Fs);U[free,:]=solver.solve(Fs[free,:]);cases={}
        for i,key in enumerate(CASES):
            cases[key]=_response(system,stored,K,U[:,i],Fs[:,i],loads_bycase[key][1],factor,rigid['cases'][key],rigid['provisional_targets'],fixed)
        failed=[key+'/'+check for key,r in cases.items() for check,passed in r['research_checks'].items() if not passed]
        variants.append(dict(stiffness_factor=factor,stiffness_status='hypothetical-unapproved; not a measured supplier or weld law',
            cases=cases,research_failed_checks=failed,research_state='failed' if failed else 'hold',
            maximum_vertical_displacement_m=max(r['maximum_vertical_displacement_m'] for r in cases.values()),
            maximum_gross_elastic_fibre_stress_pa=max(r['maximum_gross_elastic_fibre_stress_pa'] for r in cases.values()),
            maximum_joint_translation_m=max(r['maximum_joint_translation_m'] for r in cases.values()),
            maximum_joint_rotation_rad=max(r['maximum_joint_rotation_rad'] for r in cases.values()),**core.FLAGS))
    high=variants[-1];equilibrium=max(max(r['force_balance_relative'],r['moment_balance_relative'],r['free_equation_residual_relative']) for v in variants for r in v['cases'].values())
    action=max(max(row['action_reaction_force_relative'],row['action_reaction_moment_relative']) for v in variants for r in v['cases'].values() for row in r['joints'])
    high_difference=max(r['nodewise_difference_from_rigid_relative'] for r in high['cases'].values())
    normal=variants[1]['cases'];base=normal['refined_planning'];double=normal['double_vertical']
    load_scale=abs(double['maximum_vertical_displacement_m']/(2*base['maximum_vertical_displacement_m'])-1)
    checks=dict(independent_spring_beam_controls=benchmarks()['passed'],all_equilibrium=equilibrium<1e-6,
        joint_action_reaction=action<1e-8,high_stiffness_recovers_rigid_limit=high_difference<.005,
        adverse_double_load_control=load_scale<1e-7,actual_joint_calibration=None,connection_resistance_and_fatigue=None,
        supplier_or_test_stiffness_selection=None,independent_rail_acceptance=None)
    connector_definitions=[dict(id=i,joint_id=c['source']['joint_id'],first_part=c['source']['first_part'],second_part=c['source']['second_part'],
        nodes=c['nodes'],joint_point_m=c['point_m'],first_centroid_m=system['nodes_m'][c['nodes'][0]],second_centroid_m=system['nodes_m'][c['nodes'][1]],
        reference_stiffness_6x6=c['reference_stiffness'].tolist(),reference_definitions=c['reference_definitions']) for i,c in enumerate(system['connectors'])]
    if before!=_sources():raise ValueError('finite connection source changed during calculation')
    result=dict(schema='osr-carbody-finite-joint-response/1',candidate_revision=candidate['revision'],
        candidate_sha256=core.digest(candidate),rigid_frame_revision=rigid['revision'],part_revisions=deepcopy(rigid['part_revisions']),sources_sha256=before,
        refinement=2,node_identity_policy='(physical_part_id,reference_node_id); separate coincident parts retained; no rigid joint merger',
        physical_node_count=len(system['nodes_m']),node_ownership=system['node_ownership'],nodes_m=system['nodes_m'],
        connector_count=len(connector_definitions),connectors=connector_definitions,variants=variants,
        summary=[{k:v[k] for k in ('stiffness_factor','maximum_vertical_displacement_m','maximum_gross_elastic_fibre_stress_pa','maximum_joint_translation_m','maximum_joint_rotation_rad','research_state','research_failed_checks')} for v in variants],
        checks=checks,failed_checks=[k for k,v in checks.items() if v is False],held_checks=[k for k,v in checks.items() if v is None],
        state='failed' if any(v is False for v in checks.values()) else 'hold',benchmarks=benchmarks(),
        numerical_controls=dict(maximum_equilibrium_relative=equilibrium,maximum_action_reaction_relative=action,
            high_stiffness_rigid_difference_relative=high_difference,adverse_load_scaling_error=load_scale),
        provisional_targets=deepcopy(rigid['provisional_targets']),selected_stiffness_factor=None,
        interpretation='Weak-assumption failures are sensitivity findings, not proof of an actual joint failure. No hypothetical passing factor resolves unknown actual connection stiffness.',
        scope='Linear numerical sensitivity only; metre-scale motions are not predicted operable displacements. Actual owned3DRHSbeam network with finite6DOFlinear connectors and exact eccentric rigid arms; same planning mass/load/fixture hypotheses as rigid study',
        uncovered=['Measured joint6DOFmatrices and uncertainty','Issued weld/bolt/gusset geometry and resistance','Gap/slip/contact/nonlinear degradation','Joint fatigue/fire/corrosion',
            'Actual bogie/suspension and complete equipment load map','Panel/shell stiffness/local buckling and physical correlation'],
        digital_specification_complete=False,**core.FLAGS)
    result['revision']=core.digest(result);return result


@lru_cache(maxsize=2)
def _cached(candidate_bytes,rigid_bytes,source_signature):
    if core.digest(_sources())!=source_signature:raise ValueError('finite connection source changed before calculation')
    return _run(json.loads(candidate_bytes),json.loads(rigid_bytes))


def report(candidate,frame_report=None):
    controlled=frame.report(candidate)
    if frame_report is not None and core.digest(frame_report)!=core.digest(controlled):raise ValueError('stale or forged rigid frame report')
    return deepcopy(_cached(core.encoded(candidate),core.encoded(controlled),core.digest(_sources())))


def plot(result,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    values=result['summary'];factors=[v['stiffness_factor'] for v in values]
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    axes[0].plot(factors,[v['maximum_vertical_displacement_m']*1000 for v in values],marker='o')
    axes[0].axhline(result['provisional_targets']['peak_vertical_displacement_m']*1000,color='#ad542c',ls='--',label='Unapproved L/1000 study target')
    axes[0].set(xscale='log',yscale='log',xlabel='Hypothetical joint stiffness factor',ylabel='Worst case vertical displacement /mm');axes[0].legend(fontsize=8)
    axes[1].plot(factors,[v['maximum_joint_translation_m']*1000 for v in values],marker='o',label='Joint translation')
    axes[1].set(xscale='log',yscale='log',xlabel='Hypothetical joint stiffness factor',ylabel='Worst simultaneous joint translation /mm')
    fig.suptitle('Finite connection sensitivity — actual stiffness/connection acceptance remain unknown',fontsize=11)
    fig.savefig(path,dpi=120);plt.close(fig)
