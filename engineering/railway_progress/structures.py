"""Located-stock structural response under explicit frame/grillage hypotheses.

This is a finite-connection, six-DOF frame calculation, not a qualified bonded
shell, actual laminate, rail load standard or installed structural acceptance.
Native numerical workers retain source, input, logs and failed executions.
"""
from copy import deepcopy
from pathlib import Path
from math import ceil, sqrt, pi, fsum
from hashlib import sha256
import gzip
import io
import json
import os
import resource
import subprocess
import sys
import tarfile
import time

import numpy as np
import scipy
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu,eigsh
from scipy.spatial import cKDTree

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,encoded,digest
from engineering.component_registry import validate_registry
from . import FLAGS

PRODUCER='engineering/railway_progress/structures.py'
G=9.80665
PRIMARY_SOURCES=[dict(title='Hexcel Prepreg Technology',url='https://www.hexcel.com/wp-content/uploads/2026/01/Prepreg_Technology.pdf',
    scope='Manufacturer reference: typical balanced E-glass fabric tensile moduli 20/19 GPa, UD 43/8 GPa; anisotropy, layup and matrix-dependent hot/wet behaviour. Not the proposed car laminate.',
    raw_document_sha256=None,retrieval='PDF text inspected through web tool; raw download403; no authenticated material record'),
    dict(title='HexPly M56 product datasheet',url='https://www.hexcel.com/wp-content/uploads/2025/12/HexPly_M56_eu_DataSheet.pdf',
    scope='Specific unrelated M56/37%/7781 E-glass reference: typical tensile modulus25GPa, fibre volume44.6%. No property transfer or hot/wet allowable to the candidate.',raw_document_sha256=None),
    dict(title='Hulamin 6082 rolled products datasheet',url='https://www.hulamin.com/sites/default/files/downloads/6082%20Data%20Sheet.pdf',
    scope='Typical room-temperature modulus70GPa; actual temper/thickness/weld/lot allowables remain unapproved.',raw_document_sha256='17526abe0e4a1b0778a05708d7e451a487947976cc21babcdcdd86118af082a0')]
MATERIALS=dict(aluminium=dict(E1=70e9,E2=70e9,G=26e9,basis='published-room-temperature-typical'),
    GFRP=dict(E1=20e9,E2=19e9,G=4e9,basis='declared-balanced-fabric-reference-hypothesis; shear4GPa is an explicit estimate'),
    core=dict(E1=60e6,E2=60e6,G=25e6,basis='explicit-unqualified-PET-stiffness-hypothesis'),
    steel=dict(E1=200e9,E2=200e9,G=77e9,basis='explicit-room-temperature-steel-stiffness-hypothesis'))


def _vehicle(value):
    validate_registry(value['registry'])
    if value['candidate_id']!=value['registry']['candidate_id'] or value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):
        raise ValueError('Exact vehicle/registry evaluation required')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Structural input cannot grant acceptance')
    return value['registry']


def sources(vehicle,root=ROOT):
    names={**vehicle['source_sha256']}
    for name,expected in names.items():
        if digest(Path(root)/name)!=expected:raise ValueError('Vehicle structural input source is stale: '+name)
    for name in (PRODUCER,'engineering/railway_progress/__init__.py','engineering/station_rail/common.py'):
        names[name]=digest(Path(root)/name)
    if names[PRODUCER]!=digest(__file__):raise ValueError('Executing structural evaluator differs from source root')
    return dict(sorted(names.items()))


def request(vehicle,*,mesh_m=.8,joint_translation_N_m=1e9,joint_rotation_Nm_rad=1e6,
            material_scale=1.,maximum_seconds=240,memory_bytes=3*1024**3,root=ROOT):
    _vehicle(vehicle)
    if any(type(x) not in (int,float) or not np.isfinite(x) for x in (mesh_m,joint_translation_N_m,joint_rotation_Nm_rad,material_scale)):
        raise ValueError('Finite explicitly numeric structural hypotheses required')
    if (not .35<=mesh_m<=1.25 or not 1e6<=joint_translation_N_m<=1e11 or not 1e3<=joint_rotation_Nm_rad<=1e8
        or not .25<=material_scale<=1.25 or type(maximum_seconds) is not int or not 1<=maximum_seconds<=240
        or type(memory_bytes) is not int or not 1024**3<=memory_bytes<=3*1024**3):
        raise ValueError('Explicit structural mesh, connection, material and numerical bounds required')
    value=dict(schema='osr-located-structure-request/1',candidate_id=vehicle['candidate_id'],vehicle_evaluation_id=vehicle['evaluation_id'],
        vehicle=deepcopy(vehicle),mesh_sizes_m=[float(mesh_m),float(mesh_m)/2],car_number=1,
        joint_translation_N_m=float(joint_translation_N_m),joint_rotation_Nm_rad=float(joint_rotation_Nm_rad),material_scale=float(material_scale),
        contact_gap_hypothesis_m=.04,mass_bound='upper',maximum_seconds=maximum_seconds,memory_bytes=memory_bytes,
        source_sha256=sources(vehicle,root),**FLAGS)
    value['request_id']=identity(value);return value


def _validate_request(value,root=ROOT):
    rebuilt=request(value['vehicle'],mesh_m=value['mesh_sizes_m'][0],joint_translation_N_m=value['joint_translation_N_m'],
        joint_rotation_Nm_rad=value['joint_rotation_Nm_rad'],material_scale=value['material_scale'],maximum_seconds=value['maximum_seconds'],
        memory_bytes=value['memory_bytes'],root=root)
    if rebuilt!=value:raise ValueError('Exact canonical structural request/source required')
    return value


def frame_stiffness(length,A,Iy,Iz,J,E,Gs):
    """Local Euler–Bernoulli 12DOF stiffness, including axial and torsional DOF."""
    if min(length,A,Iy,Iz,J,E,Gs)<=0:raise ValueError('Positive frame section and stiffness required')
    k=np.zeros((12,12));L=length
    for pair,value in (((0,6),E*A/L),((3,9),Gs*J/L)):
        a,b=pair;k[a,a]=k[b,b]=value;k[a,b]=k[b,a]=-value
    for indices,EI,sign in (([1,5,7,11],E*Iz,1.),([2,4,8,10],E*Iy,-1.)):
        block=EI/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])
        flip=np.diag([1,sign,1,sign]);k[np.ix_(indices,indices)]=flip@block@flip
    return k


def _basis(a,b,y=None):
    x=np.asarray(b)-np.asarray(a);L=float(np.linalg.norm(x));x=x/L
    if y is None:
        axis=np.array([0.,0.,1.]) if abs(x[2])<.9 else np.array([0.,1.,0.]);y=np.cross(axis,x)
    y=np.asarray(y)-x*np.dot(x,y);y=y/np.linalg.norm(y);z=np.cross(x,y)
    return L,np.array([x,y,z])


def _skew(v):
    x,y,z=v;return np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])


def _element(nodes,element):
    L,R=_basis(nodes[element['a']],nodes[element['b']],element.get('local_y'))
    T=np.zeros((12,12))
    for i in range(4):T[3*i:3*i+3,3*i:3*i+3]=R
    k=frame_stiffness(L,element['A'],element['Iy'],element['Iz'],element['J'],element['E'],element['G'])
    return T.T@k@T,k,T


def assemble(model):
    nodes=np.asarray(model['nodes']);rr=[];cc=[];vv=[]
    def add(indices,k):
        rr.extend(np.repeat(indices,len(indices)));cc.extend(np.tile(indices,len(indices)));vv.extend(k.ravel())
    for element in model['elements']:
        indices=[6*element['a']+i for i in range(6)]+[6*element['b']+i for i in range(6)]
        add(indices,_element(nodes,element)[0])
    for link in model.get('connections',[]):
        a,b=link['a'],link['b'];point=np.asarray(link['point']);B=np.zeros((6,12))
        B[:3,:3]=np.eye(3);B[:3,3:6]=-_skew(point-nodes[a]);B[:3,6:9]=-np.eye(3);B[:3,9:]=_skew(point-nodes[b])
        B[3:,3:6]=np.eye(3);B[3:,9:]=-np.eye(3)
        add([6*a+i for i in range(6)]+[6*b+i for i in range(6)],B.T@np.diag(link['stiffness'])@B)
    size=6*len(nodes)
    return coo_matrix((vv,(rr,cc)),shape=(size,size)).tocsc()


def solve(model,load_cases):
    """Solve actual assembled matrices; retain residuals and failed mechanisms."""
    K=assemble(model);fixed=sorted(int(i) for i in model['supports']);free=np.setdiff1d(np.arange(K.shape[0]),fixed)
    diagonal=K.diagonal()[free]
    if np.any(diagonal<=0):return dict(execution='underconstrained',reason='Nonpositive unsupported DOF stiffness',zero_stiffness_dofs=free[diagonal<=0].tolist())
    scale=1/np.sqrt(diagonal);S=diags(scale);reduced=S@K[free][:,free]@S
    try:factor=splu(reduced.tocsc())
    except RuntimeError as error:return dict(execution='underconstrained',reason=str(error))
    pivots=abs(factor.U.diagonal());pivot_ratio=float(pivots.min()/max(1e-30,pivots.max()))
    if pivot_ratio<1e-14:return dict(execution='underconstrained',reason='Near-zero normalized factor pivot: mechanism or inadequate model/scaling',normalized_pivot_ratio=pivot_ratio)
    nodes=np.asarray(model['nodes']);results=[]
    for name,F,prescribed in load_cases:
        F=np.asarray(F);u=np.zeros(K.shape[0]);u[fixed]=[prescribed.get(i,0.) for i in fixed]
        rhs=F[free]-K[free][:,fixed]@u[fixed];u[free]=scale*factor.solve(scale*rhs)
        if not np.isfinite(u).all():return dict(execution='numerical-failure',reason='Nonfinite structural state')
        results.append(_response(model,K,F,u,name))
    return dict(execution='completed',nodes=len(nodes),elements=len(model['elements']),connections=len(model.get('connections',[])),
        constrained_dofs=len(fixed),normalized_pivot_ratio=pivot_ratio,cases=results,numerical_validity='Residuals evaluated; convergence and model adequacy separately assessed')


def _response(model,K,F,u,name):
    nodes=np.asarray(model['nodes']);fixed=sorted(int(i) for i in model['supports']);free=np.setdiff1d(np.arange(K.shape[0]),fixed)
    reaction=K@u-F;residual=float(np.linalg.norm(reaction[free])/max(1.,np.linalg.norm(F)))
    energy=float(u@(K@u)/2);work=float((u@F+u[fixed]@reaction[fixed])/2)
    element_by_source={}
    for element in model['elements']:
        indices=[6*element['a']+i for i in range(6)]+[6*element['b']+i for i in range(6)]
        _,k,T=_element(nodes,element);local=T@u[indices];force=k@local
        stress=abs(force[0])/element['A']+max(abs(force[4]),abs(force[10]))*element['cz']/element['Iy']+max(abs(force[5]),abs(force[11]))*element['cy']/element['Iz']
        L=float(np.linalg.norm(nodes[element['b']]-nodes[element['a']]))
        unbraced=element.get('physical_member_length_m',L)
        euler=None if element.get('representation')=='plate-grillage' else pi*pi*element['E']*min(element['Iy'],element['Iz'])/unbraced**2
        row=dict(source_occurrence_id=element['source'],axial_force_N=float(force[6]),maximum_normal_stress_proxy_Pa=float(stress),
            local_end_forces_N_Nm=force.tolist(),pinned_member_Euler_load_N=None if euler is None else float(euler),
            unsupported_length_m_hypothesis=None if euler is None else unbraced,unapproved_buckling_diagnostic_only=True,element_nodes=[element['a'],element['b']])
        previous=element_by_source.get(element['source'])
        if previous is None or row['maximum_normal_stress_proxy_Pa']>previous['maximum_normal_stress_proxy_Pa']:element_by_source[element['source']]=row
    link_by_source={}
    for link in model.get('connections',[]):
        a,b=link['a'],link['b'];point=np.asarray(link['point'])
        delta=np.r_[u[6*a:6*a+3]+np.cross(u[6*a+3:6*a+6],point-nodes[a])-u[6*b:6*b+3]-np.cross(u[6*b+3:6*b+6],point-nodes[b]),u[6*a+3:6*a+6]-u[6*b+3:6*b+6]]
        forces=np.asarray(link['stiffness'])*delta
        key=tuple(link['source_pair'])
        if key not in link_by_source:link_by_source[key]=dict(source_pair=link['source_pair'],force_N=[0.,0.,0.],moment_about_registry_origin_Nm=[0.,0.,0.],
            maximum_relative_translation_m=0.,maximum_relative_rotation_rad=0.,maximum_point_force_N=0.,point_count=0,strain_energy_J=0.,approved_joint_margin=None)
        aggregate=link_by_source[key]
        aggregate['force_N']=(np.asarray(aggregate['force_N'])+forces[:3]).tolist()
        aggregate['moment_about_registry_origin_Nm']=(np.asarray(aggregate['moment_about_registry_origin_Nm'])+forces[3:]+np.cross(point,forces[:3])).tolist()
        aggregate['maximum_relative_translation_m']=max(aggregate['maximum_relative_translation_m'],float(np.linalg.norm(delta[:3])))
        aggregate['maximum_relative_rotation_rad']=max(aggregate['maximum_relative_rotation_rad'],float(np.linalg.norm(delta[3:])))
        aggregate['maximum_point_force_N']=max(aggregate['maximum_point_force_N'],float(np.linalg.norm(forces[:3])))
        aggregate['point_count']+=1;aggregate['strain_energy_J']+=float(np.dot(forces,delta)/2)
    displacement=u.reshape(-1,6);reactions=np.zeros_like(u);reactions[fixed]=reaction[fixed];total=(F+reactions).reshape(-1,6)
    imbalance_force=total[:,:3].sum(axis=0);imbalance_moment=(total[:,3:]+np.cross(nodes,total[:,:3])).sum(axis=0)
    return dict(name=name,maximum_translation_m=float(np.linalg.norm(displacement[:,:3],axis=1).max()),
        maximum_rotation_rad=float(np.linalg.norm(displacement[:,3:],axis=1).max()),displacements_m_rad=displacement.tolist(),
        support_reactions=[dict(dof=i,reaction=float(reaction[i])) for i in fixed],free_relative_residual=residual,
        strain_energy_J=energy,external_plus_support_work_J=work,relative_energy_residual=abs(energy-work)/max(1.,abs(energy)),
        force_balance_residual_N=imbalance_force.tolist(),moment_balance_residual_Nm=imbalance_moment.tolist(),
        elements=list(element_by_source.values()),connections=list(link_by_source.values()),
        element_response_scope='Worst-stress witness per source part; complete model and displacement field preserve every element',approved_strength_margin=None,approved_deflection_limit_m=None,
        small_displacement_domain_suspect=bool(np.linalg.norm(displacement[:,:3],axis=1).max()/max(1.,float(np.ptp(nodes,axis=0).max()))>.01 or np.linalg.norm(displacement[:,3:],axis=1).max()>.1),
        kinematic_diagnostic_basis='Advisory linear-kinematic sensitivity, not an approved clearance/strength/body rejection rule')


def build_model(value,mesh_m,joint_translation_N_m=1e9,joint_rotation_Nm_rad=1e6,material_scale=1.,gap=.04):
    registry=_vehicle(value);parts={p['physical_definition_id']:p for p in registry['parts']}
    materials={m['material_id']:m for m in registry['materials']};nodes=[];elements=[];groups=[];car=[]
    for occurrence in registry['occurrences']:
        if not occurrence['occurrence_id'].startswith('car-1/'):continue
        part=parts[occurrence['part_definition_id']];car.append((occurrence,part))
        name=part['part_id'].lower()
        structural=(any(f in part['functions'] for f in ('primary-body','bogie-interfaces')) and part['geometry']['kind']=='box'
            and not any(token in name for token in ('adhesive','bondline','-shaft','-head','-nut','-washer','captive','retainer','service-panel')))
        if not structural:continue
        d=np.asarray(part['geometry']['dimensions_m']);matrix=np.asarray(occurrence['transform']);R=matrix[:3,:3];centre=matrix[:3,3]
        grade=materials[part['material_id']]['grade_id'];kind='core' if grade.startswith('PET') else 'GFRP' if grade.startswith('GFRP') else 'aluminium' if grade.startswith('AL-') else 'steel'
        material=MATERIALS[kind];indices=np.argsort(-d);long,other,thin=[int(i) for i in indices]
        group=dict(source=occurrence['occurrence_id'],nodes=[],lower=(centre-np.abs(R)@d/2).tolist(),upper=(centre+np.abs(R)@d/2).tolist(),material_kind=kind)
        def node(local):
            index=len(nodes);nodes.append((centre+R@np.asarray(local)).tolist());group['nodes'].append(index);return index
        def member(a,b,width,depth,E,local_y,plate=False):
            A=width*depth;Iy=width*depth**3/12;Iz=depth*width**3/12
            aa=max(width,depth);bb=min(width,depth);J=width*depth**3/6 if plate else aa*bb**3*(1/3-.21*bb/aa*(1-bb**4/(12*aa**4)))
            elements.append(dict(a=a,b=b,A=A,Iy=Iy,Iz=Iz,J=J,E=E*material_scale,G=material['G']*material_scale,
                cy=width/2,cz=depth/2,local_y=local_y.tolist(),source=group['source'],physical_member_length_m=float(d[long]),
                representation='plate-grillage' if plate else 'frame'))
        if d[other]>=8*d[thin]:
            na=max(2,int(ceil(d[long]/mesh_m)));nb=max(2,int(ceil(d[other]/mesh_m)))
            grid={}
            for i in range(na+1):
                for j in range(nb+1):
                    local=np.zeros(3);local[long]=-d[long]/2+d[long]*i/na;local[other]=-d[other]/2+d[other]*j/nb;grid[i,j]=node(local)
            for i in range(na):
                for j in range(nb+1):member(grid[i,j],grid[i+1,j],d[other]/nb*(.5 if j in (0,nb) else 1.),d[thin],material['E1'],R[:,other],True)
            for j in range(nb):
                for i in range(na+1):member(grid[i,j],grid[i,j+1],d[long]/na*(.5 if i in (0,na) else 1.),d[thin],material['E2'],R[:,long],True)
            group['mass_weights']=[(.5 if i in (0,na) else 1.)*(.5 if j in (0,nb) else 1.) for i in range(na+1) for j in range(nb+1)]
            group['representation']='orthogonal-plate-grillage-not-full-shell'
        else:
            n=max(2,int(ceil(d[long]/mesh_m)));n+=n%2;path=[]
            for i in range(n+1):
                local=np.zeros(3);local[long]=-d[long]/2+d[long]*i/n;path.append(node(local))
            cross=[i for i in range(3) if i!=long]
            for a,b in zip(path[:-1],path[1:]):member(a,b,d[cross[0]],d[cross[1]],material['E1'],R[:,cross[0]])
            group['mass_weights']=[.5]+[1.]*(n-1)+[.5]
            group['representation']='3D-Euler-Bernoulli-frame'
        groups.append(group)
    if len(nodes)>12000:raise ValueError('Structural mesh node budget exceeded')
    connections=[];adjacency={i:set() for i in range(len(groups))}
    xyz=np.asarray(nodes)
    for i,a in enumerate(groups):
        alo,ahi=np.array(a['lower']),np.array(a['upper'])
        for j,b in enumerate(groups[i+1:],i+1):
            blo,bhi=np.array(b['lower']),np.array(b['upper']);distance=np.maximum(np.maximum(alo-bhi,blo-ahi),0.)
            if np.linalg.norm(distance)>gap:continue
            lower=np.maximum(alo,blo);upper=np.minimum(ahi,bhi);mid=(lower+upper)/2
            candidates=[n for n in a['nodes'] if np.all(xyz[n]>=np.minimum(lower,upper)-mesh_m*.15) and np.all(xyz[n]<=np.maximum(lower,upper)+mesh_m*.15)]
            if not candidates:candidates=[min(a['nodes'],key=lambda n:np.linalg.norm(xyz[n]-mid))]
            tree=cKDTree(xyz[b['nodes']]);pairs=set()
            for aa in candidates:
                bb=b['nodes'][int(tree.query(xyz[aa])[1])];pairs.add((aa,bb))
            for aa,bb in sorted(pairs):
                point=(xyz[aa]+xyz[bb])/2
                connections.append(dict(a=aa,b=bb,point=point.tolist(),stiffness=[joint_translation_N_m/len(pairs)]*3+[joint_rotation_Nm_rad/len(pairs)]*3,
                    source_pair=[a['source'],b['source']],physical_gap_m=float(np.linalg.norm(distance)),
                    joint_geometry_and_stiffness_qualified=False))
            adjacency[i].add(j);adjacency[j].add(i)
    supports={};support_nodes=[]
    for point in value['interfaces']['body_secondary_hardpoint_positions_m']:
        candidates=[group for group in groups if 'body-bogie-hardpoint' in group['source']]
        indices=[n for group in candidates for n in group['nodes']]
        if not indices:raise ValueError('Actual four body hardpoint geometries required')
        n=min(indices,key=lambda n:np.linalg.norm(xyz[n]-point));support_nodes.append(n);supports[6*n+2]=0.
    supports[6*support_nodes[0]]=0.;supports[6*support_nodes[0]+1]=0.;supports[6*support_nodes[2]+1]=0.
    remaining=set(adjacency);components=[]
    while remaining:
        seed=remaining.pop();component={seed};front=[seed]
        while front:
            n=front.pop()
            for m in adjacency[n]&remaining:remaining.remove(m);component.add(m);front.append(m)
        components.append(sorted(component))
    model=dict(nodes=nodes,elements=elements,connections=connections,supports={str(i):x for i,x in supports.items()},groups=groups,
        source_part_occurrences=len(car),source_structural_parts=len(groups),connectivity_components=[[groups[i]['source'] for i in c] for c in components],
        support_nodes=support_nodes,mesh_m=mesh_m,scope='Actual sized stock represented by 3D frame/plate grillage and unapproved finite joint laws; no full-shell or laminate qualification')
    return model,car


def load_cases(value,model,car):
    nodes=np.asarray(model['nodes']);tree=cKDTree(nodes);size=6*len(nodes);base=np.zeros(size);accounted_mass=0.;bindings=[]
    def apply(F,position,force):
        n=int(tree.query(position)[1]);offset=np.asarray(position)-nodes[n];F[6*n:6*n+3]+=force;F[6*n+3:6*n+6]+=np.cross(offset,force)
    structural_groups={group['source']:group for group in model['groups']}
    for occurrence,part in car:
        mass=part['mass']['upper_bound_kg']
        if mass is None:raise ValueError('Every installed mass needs an explicit upper bound for this conditional case')
        position=np.asarray(occurrence['transform'])[:3,3]
        group=structural_groups.get(occurrence['occurrence_id'])
        if group is None:apply(base,position,[0.,0.,-mass*G])
        else:
            total=fsum(group['mass_weights'])
            for node,weight in zip(group['nodes'],group['mass_weights']):base[6*node+2]-=mass*G*weight/total
        accounted_mass+=mass
        bindings.append(dict(occurrence_id=occurrence['occurrence_id'],mass_upper_kg=mass,load_at_bounded_envelope_centre=True))
    normals=base.copy();crowd=base.copy();seats=[]
    for occurrence,part in car:
        if 'seat-pan' in occurrence['occurrence_id']:seats.append(np.asarray(occurrence['transform'])[:3,3])
        elif 'two-place-wall-bench' in occurrence['occurrence_id']:
            q=np.asarray(occurrence['transform'])[:3,3];seats.extend([q+[-.24,0.,0.],q+[.24,0.,0.]])
    seats.extend(np.asarray(r['center_m']) for r in value['interfaces']['wheelchair_spaces_per_car'])
    if len(seats)!=46:raise ValueError('Actual44fixedseats+2wheelchair positions required')
    for q in seats:apply(normals,q,[0.,0.,-75*G])
    for x in np.linspace(.5,16.5,16):
        for y in np.linspace(-1.15,1.15,10):apply(crowd,[x,y,1.65],[0.,0.,-75*G])
    cases=[('empty-upper',base,{}),('normal-upper',normals,{}),('crowd-160-upper',crowd,{})]
    for title,token,axis,accel in (('service-brake-normal',None,0,.6),('door-lateral-inertia','door-',1,.6),
        ('HVAC-lateral-inertia','HVAC-',1,.6),('solar-lateral-inertia','solar-',1,.6)):
        F=normals.copy()
        for occurrence,part in car:
            if token is None or token in occurrence['occurrence_id']:
                force=np.zeros(3);force[axis]=part['mass']['upper_bound_kg']*accel
                apply(F,np.asarray(occurrence['transform'])[:3,3],force)
        cases.append((title,F,{}))
    for title,token,demand in (('fin-whole-train-demand','passive-aluminium-fin',6*(accounted_mass+3450)*.4),
        ('coupler-five-trailing-cars-demand','coupler-drawgear',5*(accounted_mass+3450)*.6)):
        F=normals.copy();targets=[o for o,p in car if token in o['occurrence_id']]
        if not targets:raise ValueError('Actual fin and coupling interfaces required')
        target=targets[-1];apply(F,np.asarray(target['transform'])[:3,3],[demand,0.,0.]);cases.append((title,F,{}))
    twist={6*model['support_nodes'][-1]+2:.003};cases.append(('support-twist-3mm-hypothesis',normals.copy(),twist))
    return cases,dict(upper_mass_kg=accounted_mass,normal_people=46,crowd_people=160,people_mass_kg=75.,
        installed_mass_is_qualified=False,mass_bindings=bindings,
        caveats=['Mass bounds/envelope-centre hypotheses; actual internal CG remains unknown',
            'Interface inertial and fin/coupler demand loads are hypotheses, not approved load standards or available motor thrust',
            'Hardpoints have fixed vertical support positions with six rigid-body freedoms restrained; actual suspension stiffness and rail dynamics remain open'])


def benchmarks():
    """Analytic cantilever/torsion and independent Navier-series plate controls."""
    E=70e9;Gs=26e9;A=.01;Iy=1e-5;Iz=2e-5;J=1e-5;L=2.
    element=dict(a=0,b=1,A=A,Iy=Iy,Iz=Iz,J=J,E=E,G=Gs,cy=.1,cz=.1,source='independent-cantilever-control')
    model=dict(nodes=[[0.,0.,0.],[L,0.,0.]],elements=[element],connections=[],supports={str(i):0. for i in range(6)})
    vertical=np.zeros(12);vertical[8]=-1000.;torsion=np.zeros(12);torsion[9]=100.
    result=solve(model,[('cantilever',vertical,{}),('torsion',torsion,{})])
    deflection=abs(result['cases'][0]['displacements_m_rad'][1][2]);rotation=abs(result['cases'][1]['displacements_m_rad'][1][3])
    controls=dict(cantilever=dict(calculated_tip_m=deflection,analytic_tip_m=1000*L**3/(3*E*Iy)),
        torsion=dict(calculated_rotation_rad=rotation,analytic_rotation_rad=100*L/(Gs*J)))
    plates=[];t=.01;q=1000.;D=E*t**3/12
    reference=16*q/(pi**6*D)*fsum((-1.)**((m-1)//2+(n-1)//2)/(m*n*(m*m+n*n)**2) for m in range(1,64,2) for n in range(1,64,2))
    for divisions in (8,16):
        index=lambda i,j:i*(divisions+1)+j
        nodes=[[i/divisions,j/divisions,0.] for i in range(divisions+1) for j in range(divisions+1)]
        elements=[];supports={};force=np.zeros(6*len(nodes))
        for i in range(divisions+1):
            for j in range(divisions+1):
                k=index(i,j)
                for d in (0,1,5):supports[str(6*k+d)]=0.
                if i in (0,divisions) or j in (0,divisions):supports[str(6*k+2)]=0.
                force[6*k+2]=-q/divisions**2*(.5 if i in (0,divisions) else 1.)*(.5 if j in (0,divisions) else 1.)
        for direction in (0,1):
            for a in range(divisions):
                for b in range(divisions+1):
                    width=1/divisions*(.5 if b in (0,divisions) else 1.)
                    first=index(a,b) if direction==0 else index(b,a);second=index(a+1,b) if direction==0 else index(b,a+1)
                    elements.append(dict(a=first,b=second,A=width*t,Iy=width*t**3/12,Iz=t*width**3/12,J=width*t**3/6,
                        E=E,G=E/2,cy=width/2,cz=t/2,local_y=[0.,1.,0.] if direction==0 else [1.,0.,0.],source='plate-control'))
        calculated=solve(dict(nodes=nodes,elements=elements,connections=[],supports=supports),[('plate',force,{})])['cases'][0]['maximum_translation_m']
        plates.append(dict(divisions=divisions,calculated_centre_m=calculated,Navier_series_centre_m=reference,relative_error=abs(calculated-reference)/reference))
    controls['plate']=dict(results=plates,domain='Isotropic nu=0 thin simply-supported square under uniform pressure; not actual sandwich/core shear or GFRP shell qualification')
    controls['scope']='Mathematical method comparisons only; no body, joint, material or physical approval'
    return controls


def evaluate(vehicle,*,root=ROOT,**options):
    r=request(vehicle,root=root,**options);results=[];started=time.monotonic()
    for mesh in r['mesh_sizes_m']:
        if time.monotonic()-started>r['maximum_seconds']:raise TimeoutError('Structural numerical budget exceeded')
        model,car=build_model(vehicle,mesh,r['joint_translation_N_m'],r['joint_rotation_Nm_rad'],r['material_scale'],r['contact_gap_hypothesis_m'])
        cases,loads=load_cases(vehicle,model,car);response=solve(model,cases)
        results.append(dict(mesh_m=mesh,model=model,loads=loads,response=response))
    complete=all(x['response']['execution']=='completed' for x in results)
    refinement=None
    if complete:
        refinement=[dict(case=a['name'],coarse_max_translation_m=a['maximum_translation_m'],fine_max_translation_m=b['maximum_translation_m'],
            relative_change=None if b['maximum_translation_m']==0 else abs(a['maximum_translation_m']-b['maximum_translation_m'])/abs(b['maximum_translation_m']))
            for a,b in zip(results[0]['response']['cases'],results[1]['response']['cases'])]
    value=dict(schema='osr-located-structure-evaluation/1',candidate_id=vehicle['candidate_id'],vehicle_evaluation_id=vehicle['evaluation_id'],
        request_id=r['request_id'],execution='completed' if complete else 'model-or-numerical-hold',results=results,refinement=refinement,
        material_models=MATERIALS,primary_references=PRIMARY_SOURCES,approved_strength_allowables=None,approved_joint_allowables=None,
        approved_deflection_or_functional_clearance_limits=None,hot_wet_retention=None,fatigue_law=None,actual_laminate_schedule=None,
        unsupported_domains=['actual bonded-shell transverse/core shear','local peel/bearing/fastener strength','orthotropic ply failure','nonlinear/global shell buckling','fatigue/crash/fire','actual suspension/contact dynamics'],
        conditional_calculation_completed=complete,whole_body_qualification=False,engineering_screen='pending-approved-model-material-joint-and-interface-evidence',
        diagnosis=[dict(kind='connectivity-or-mechanism',mesh_m=x['mesh_m'],components=len(x['model']['connectivity_components']),
            action='Revise actual joint/support geometry or improve inadequately represented bonded-shell evaluator; do not reject a shell from its grillage alone') for x in results],
        physical_revision_requests=['Resolve each provisional contact/offset connection with counted manufactured joint geometry and approved stiffness/strength',
            'Supply actual laminate plies, directional/hot-wet/fire/fatigue data and face/core/bond shear model',
            'Refine frame/shell mesh and independently correlate with component/body measurements before selecting a body'],
        method_benchmarks=benchmarks(),source_sha256=r['source_sha256'],**FLAGS)
    value['evaluation_id']=identity(value);return value


def _tool():
    import scipy.sparse.linalg._dsolve._superlu as superlu
    return dict(python=sys.version,python_sha256=digest(sys.executable),numpy=np.__version__,scipy=scipy.__version__,superlu_sha256=digest(superlu.__file__))


def run(r,output,*,root=ROOT):
    _validate_request(r,root);folder=Path(output)
    if folder.exists():raise ValueError('Fresh immutable structural run required')
    folder.mkdir(parents=True);(folder/'input.json').write_bytes(encoded(r))
    data=io.BytesIO()
    with tarfile.open(fileobj=data,mode='w') as archive:
        for name,expected in r['source_sha256'].items():
            raw=(Path(root)/name).read_bytes()
            if sha256(raw).hexdigest()!=expected:raise ValueError('Structural source changed')
            info=tarfile.TarInfo(name);info.size=len(raw);info.mtime=0;archive.addfile(info,io.BytesIO(raw))
    (folder/'input-sources.tar.gz').write_bytes(gzip.compress(data.getvalue(),mtime=0))
    def limit():resource.setrlimit(resource.RLIMIT_AS,(r['memory_bytes'],r['memory_bytes']))
    try:
        proc=subprocess.run([sys.executable,'-m','engineering.railway_progress.structures','--worker',str(folder.resolve())],cwd=root,
            capture_output=True,timeout=r['maximum_seconds']+5,preexec_fn=limit,
            env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
        (folder/'stdout.log').write_bytes(proc.stdout);(folder/'stderr.log').write_bytes(proc.stderr)
        result=json.loads((folder/'worker-result.json').read_bytes()) if (folder/'worker-result.json').is_file() else dict(execution='tool-error',returncode=proc.returncode,**FLAGS)
    except subprocess.TimeoutExpired as error:
        (folder/'stdout.log').write_bytes(error.stdout or b'');(folder/'stderr.log').write_bytes(error.stderr or b'');result=dict(execution='interrupted',reason='Structural worker deadline exceeded',**FLAGS)
    if sources(r['vehicle'],root)!=r['source_sha256']:raise ValueError('Structural source changed during execution')
    result.update(candidate_id=r['candidate_id'],request_id=r['request_id'],source_sha256=r['source_sha256'])
    result['run_evaluation_id']=identity(result);(folder/'result.json').write_bytes(encoded(result))
    manifest=dict(schema='osr-located-structure-package/1',candidate_id=r['candidate_id'],request_id=r['request_id'],evaluation_id=result['run_evaluation_id'],
        source_sha256=r['source_sha256'],files_sha256={p.name:digest(p) for p in folder.iterdir()},**FLAGS)
    manifest['manifest_id']=identity(manifest);(folder/'manifest.json').write_bytes(encoded(manifest));return result


def verify(output,*,root=ROOT,require_current_tool=True):
    if type(require_current_tool) is not bool:raise ValueError('Explicit tool policy required')
    folder=Path(output)
    if folder.is_symlink() or any(not p.is_file() or p.is_symlink() for p in folder.iterdir()):raise ValueError('Ordinary structural package required')
    manifest=json.loads((folder/'manifest.json').read_bytes());r=json.loads((folder/'input.json').read_bytes());_validate_request(r,root)
    result=json.loads((folder/'result.json').read_bytes())
    if (manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
        or manifest.get('files_sha256')!={p.name:digest(p) for p in folder.iterdir() if p.name!='manifest.json'}
        or manifest.get('source_sha256')!=r['source_sha256'] or result.get('run_evaluation_id')!=identity({k:v for k,v in result.items() if k!='run_evaluation_id'})
        or result.get('candidate_id')!=r['candidate_id'] or any(manifest.get(k) is not False or result.get(k) is not False for k in FLAGS)):
        raise ValueError('Structural source/payload/identity/disposition differs')
    worker=json.loads((folder/'worker-result.json').read_bytes()) if (folder/'worker-result.json').is_file() else None
    if worker is not None:
        if worker.get('evaluation_id')!=identity({k:v for k,v in worker.items() if k!='evaluation_id'}):raise ValueError('Structural worker evaluation identity differs')
        if worker.get('actual_address_space_limit_bytes')!=r['memory_bytes'] or worker.get('OPENBLAS_NUM_THREADS')!='1' or worker.get('OMP_NUM_THREADS')!='1':raise ValueError('Actual structural worker budget differs')
        expected={**worker,'candidate_id':r['candidate_id'],'request_id':r['request_id'],'source_sha256':r['source_sha256']}
        if {k:v for k,v in result.items() if k!='run_evaluation_id'}!=expected:raise ValueError('Structural worker/result binding differs')
    if require_current_tool and worker is not None and worker.get('tool')!=_tool():raise ValueError('Current structural numerical tool differs; no exact reuse')
    _verify_retained_sources(folder,r['source_sha256'],root)
    if worker is not None and worker.get('results') is not None:
        if worker.get('actual_address_space_limit_bytes')!=r['memory_bytes'] or worker.get('OPENBLAS_NUM_THREADS')!='1' or worker.get('OMP_NUM_THREADS')!='1':
            raise ValueError('Actual structural worker resource contract differs')
        _verify_responses(r,worker)
    if manifest.get('schema')!='osr-located-structure-package/1' or manifest.get('candidate_id')!=r['candidate_id'] or manifest.get('request_id')!=r['request_id'] or manifest.get('evaluation_id')!=result['run_evaluation_id']:
        raise ValueError('Structural manifest candidate/evaluation binding differs')
    allowed={'input.json','input-sources.tar.gz','stdout.log','stderr.log','result.json','manifest.json','worker-result.json'}
    if set(p.name for p in folder.iterdir())-allowed:raise ValueError('Unexpected structural artifact')
    return dict(verified=True,candidate_id=r['candidate_id'],evaluation_id=result['run_evaluation_id'],execution=result['execution'],
        numerical_replayed=False,factorization_reexecuted=False,
        matrix_response_arithmetic_recomputed=bool(worker and any(x['response']['execution']=='completed' for x in worker.get('results',[]))),physical_qualification=False,**FLAGS)


def _close(actual,expected):
    if isinstance(expected,dict):return isinstance(actual,dict) and set(actual)==set(expected) and all(_close(actual[k],v) for k,v in expected.items())
    if isinstance(expected,list):return isinstance(actual,list) and len(actual)==len(expected) and all(_close(a,b) for a,b in zip(actual,expected))
    if type(expected) in (int,float) and type(actual) in (int,float):return np.isfinite(actual) and abs(actual-expected)<=1e-8*max(1.,abs(expected))
    return type(actual)==type(expected) and actual==expected


def _verify_retained_sources(folder,source,root):
    with gzip.open(folder/'input-sources.tar.gz','rb') as stream:raw=stream.read(64*1024**2+1)
    if len(raw)>64*1024**2:raise ValueError('Structural source archive exceeds budget')
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
        seen=set()
        for member in archive:
            if not member.isfile() or member.name not in source or member.name in seen or Path(member.name).is_absolute() or '..' in Path(member.name).parts:
                raise ValueError('Exact ordinary source archive required')
            seen.add(member.name);data=archive.extractfile(member).read()
            if sha256(data).hexdigest()!=source[member.name] or data!=(Path(root)/member.name).read_bytes():raise ValueError('Retained structural source bytes differ')
        if seen!=set(source):raise ValueError('Structural source archive missing inputs')


def _verify_responses(r,worker):
    if len(worker['results'])!=len(r['mesh_sizes_m']):raise ValueError('Structural refinement inventory differs')
    for sample,mesh in zip(worker['results'],r['mesh_sizes_m']):
        model,car=build_model(r['vehicle'],mesh,r['joint_translation_N_m'],r['joint_rotation_Nm_rad'],r['material_scale'],r['contact_gap_hypothesis_m'])
        cases,loads=load_cases(r['vehicle'],model,car)
        if not _close(sample['model'],model) or not _close(sample['loads'],loads) or sample['mesh_m']!=mesh:
            raise ValueError('Structural geometry, mass/interface loading or mesh semantic replay differs')
        response=sample['response']
        if response['execution']=='completed':
            if len(response['cases'])!=len(cases):raise ValueError('Structural load cases missing')
            K=assemble(model)
            for saved,(name,F,prescribed) in zip(response['cases'],cases):
                u=np.asarray(saved['displacements_m_rad']).ravel()
                if u.shape!=(6*len(model['nodes']),) or not np.isfinite(u).all():raise ValueError('Finite full structural displacement field required')
                for dof in model['supports']:
                    if abs(u[int(dof)]-prescribed.get(int(dof),0.))>1e-10:raise ValueError('Structural support displacement differs')
                if not _close(saved,_response(model,K,F,u,name)):raise ValueError('Structural force/energy/reaction arithmetic differs')


def _worker(folder):
    folder=Path(folder);r=json.loads((folder/'input.json').read_bytes())
    try:
        _validate_request(r)
        result=evaluate(r['vehicle'],mesh_m=r['mesh_sizes_m'][0],joint_translation_N_m=r['joint_translation_N_m'],
            joint_rotation_Nm_rad=r['joint_rotation_Nm_rad'],material_scale=r['material_scale'],
            maximum_seconds=r['maximum_seconds'],memory_bytes=r['memory_bytes'])
    except Exception as error:result=dict(execution='held',reason=type(error).__name__+': '+str(error),**FLAGS)
    result.update(candidate_id=r['candidate_id'],request_id=r['request_id'],source_sha256=r['source_sha256'])
    result.pop('evaluation_id',None)
    result['tool']=_tool();result['actual_address_space_limit_bytes']=resource.getrlimit(resource.RLIMIT_AS)[0]
    result['OPENBLAS_NUM_THREADS']=os.environ.get('OPENBLAS_NUM_THREADS');result['OMP_NUM_THREADS']=os.environ.get('OMP_NUM_THREADS')
    result['evaluation_id']=identity(result)
    (folder/'worker-result.json').write_bytes(encoded(result))


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='--worker':raise SystemExit('Use structural request/run/verify')
    _worker(sys.argv[2])
