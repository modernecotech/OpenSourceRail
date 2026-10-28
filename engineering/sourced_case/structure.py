"""Source-bound layered sandwich and finite-footprint structural investigations.

This replaces no frozen result. Composite action is an explicit *conditional*
face/core hypothesis. Panel responses, rail-only whole-length demand responses,
and missing manufactured load paths are different findings, never acceptance.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
from math import ceil, fsum
import io
import json
import os
import resource
import subprocess
import sys
import tarfile
import time

import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity, digest
from engineering.component_registry import validate_registry

PRODUCER='engineering/sourced_case/structure.py'
DATA='engineering/sourced_case/data/structural-sources.json'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False)
G=9.80665
FILES={'input.json','sources.tar','stdout.log','stderr.log','result.json','manifest.json'}


def primary_sources(root=ROOT):
    value=json.loads((Path(root)/DATA).read_text())
    if value['schema']!='osr-primary-structural-sources/1':raise ValueError('Primary source catalogue required')
    return value


def _vehicle(vehicle):
    validate_registry(vehicle['registry'])
    if vehicle['candidate_id']!=vehicle['registry']['candidate_id'] or vehicle['evaluation_id']!=identity({k:v for k,v in vehicle.items() if k!='evaluation_id'}):
        raise ValueError('Exact same-candidate vehicle evaluation required')
    if any(vehicle.get(k) is not False for k in FLAGS):raise ValueError('Research inputs cannot inherit acceptance')
    return vehicle['registry']


def sources(vehicle,root=ROOT):
    names=dict(vehicle['source_sha256'])
    for name,expected in names.items():
        if digest(Path(root)/name)!=expected:raise ValueError('Stale vehicle source '+name)
    names[PRODUCER]=digest(Path(root)/PRODUCER);names[DATA]=digest(Path(root)/DATA)
    names['engineering/station_rail/common.py']=digest(Path(root)/'engineering/station_rail/common.py')
    if names[PRODUCER]!=digest(__file__):raise ValueError('Executing structure source differs from declared root')
    return dict(sorted(names.items()))


def request(vehicle,*,divisions=12,face_E_GPa_hypothesis=20.,core_direction='unoriented-worst',maximum_seconds=240,
            memory_bytes=3*1024**3,root=ROOT):
    _vehicle(vehicle)
    if type(divisions) is not int or not 4<=divisions<=32:raise ValueError('Bounded 4..32 base mesh divisions required')
    if type(face_E_GPa_hypothesis) not in (float,int) or not 10<=face_E_GPa_hypothesis<=30:raise ValueError('Explicit generic GFRP face hypothesis 10..30GPa required')
    if core_direction not in ('unoriented-worst','0deg','90deg'):raise ValueError('Explicit Kerdyn shear orientation required')
    if type(maximum_seconds) is not int or not 1<=maximum_seconds<=240 or type(memory_bytes) is not int or not 1024**3<=memory_bytes<=3*1024**3:
        raise ValueError('At most240s/3GiB numerical resources required')
    value=dict(schema='osr-layered-structure-request/1',vehicle=deepcopy(vehicle),candidate_id=vehicle['candidate_id'],
        vehicle_evaluation_id=vehicle['evaluation_id'],divisions=[divisions,2*divisions],face_E_GPa_hypothesis=float(face_E_GPa_hypothesis),
        core_direction=core_direction,mass_bound='upper',maximum_seconds=maximum_seconds,memory_bytes=memory_bytes,
        source_sha256=sources(vehicle,root),**FLAGS)
    value['request_id']=identity(value);return value


def _validate_request(value,root=ROOT):
    if request(value['vehicle'],divisions=value['divisions'][0],face_E_GPa_hypothesis=value['face_E_GPa_hypothesis'],core_direction=value['core_direction'],
               maximum_seconds=value['maximum_seconds'],memory_bytes=value['memory_bytes'],root=root)!=value:
        raise ValueError('Exact canonical source-bound request required')


def layered_section(faces,core_thickness_m,width_m,core_G_Pa):
    """Axial face integration + core shear energy; core axial E is unknown.

    faces: [{z_m, thickness_m, E_Pa}]. The core is a shear carrier, not a
    falsely isotropic material with Ez used as longitudinal E. EA/EI include
    exact face self-inertia and parallel axes. Thin-face core-only shear law
    integrates tau=V/(b*h) through actual core thickness: S=G*b*h²/tc.
    """
    if len(faces)!=2 or min(core_thickness_m,width_m,core_G_Pa)<=0:raise ValueError('Two positive separated faces/core required')
    for f in faces:
        if min(f['thickness_m'],f['E_Pa'])<=0 or not np.isfinite([f['z_m'],f['thickness_m'],f['E_Pa']]).all():raise ValueError('Finite positive face properties required')
    a,b=sorted(faces,key=lambda f:f['z_m']);h=b['z_m']-a['z_m']
    if h<core_thickness_m:raise ValueError('Face centres cannot lie inside the core')
    EA=fsum(f['E_Pa']*width_m*f['thickness_m'] for f in faces)
    neutral=fsum(f['E_Pa']*width_m*f['thickness_m']*f['z_m'] for f in faces)/EA
    terms=[f['E_Pa']*width_m*(f['thickness_m']**3/12+f['thickness_m']*(f['z_m']-neutral)**2) for f in faces]
    separated=fsum(terms);independent=fsum(f['E_Pa']*width_m*f['thickness_m']**3/12 for f in faces)
    return dict(EA_N=EA,EI_Nm2=separated,neutral_axis_m=neutral,core_shear_stiffness_N=core_G_Pa*width_m*h*h/core_thickness_m,
        face_centre_separation_m=h,independent_faces_EI_Nm2=independent,composite_to_independent_EI_ratio=separated/independent,
        core_longitudinal_E_Pa=None,core_axial_EI_term_included=False,
        assumptions=['Perfect face-core shear transfer for this conditional calculation; bond continuity is separately audited',
            'Core-only shear-energy approximation; face shear/adhesive compliance and nonlinear indentation remain unmodelled'],
        approved_strength_allowable_Pa=None)


def timoshenko_stiffness(L,EI,S):
    if min(L,EI,S)<=0:raise ValueError('Positive Timoshenko properties required')
    phi=12*EI/(S*L*L)
    return EI/(L**3*(1+phi))*np.array([[12.,6*L,-12.,6*L],[6*L,(4+phi)*L*L,-6*L,(2-phi)*L*L],
        [-12.,-6*L,12.,-6*L],[6*L,(2-phi)*L*L,-6*L,(4+phi)*L*L]])


def beam_response(length_m,EI,S,point_loads=(),uniform_N_m=0.,supports=(),bearing_patches=(),divisions=16,extra_nodes=(),point_moments=()):
    """Actual 2DOF shear-flexible finite elements; finite bearing springs.

    Point loads use work-conjugate linear interpolation preserving resultant
    and moment. Mesh refinement assesses that approximation. No axial, lateral,
    torsional, shell or skin-wrinkling qualification is implied.
    """
    positions=set(float(x) for x in np.linspace(0.,length_m,divisions+1))
    positions.update(float(x) for x in supports);positions.update(float(x) for x in extra_nodes)
    for p in bearing_patches:positions.update([float(p['a_m']),float((p['a_m']+p['b_m'])/2),float(p['b_m'])])
    if not positions or min(positions)<-1e-10 or max(positions)>length_m+1e-10:raise ValueError('All supports within physical member required')
    x=np.array(sorted(positions));size=2*len(x);rows=[];cols=[];values=[];F=np.zeros(size);elements=[]
    for i,L in enumerate(np.diff(x)):
        if L<1e-9:raise ValueError('Degenerate beam element')
        k=timoshenko_stiffness(float(L),EI,S);indices=[2*i,2*i+1,2*i+2,2*i+3]
        rows.extend(np.repeat(indices,4));cols.extend(np.tile(indices,4));values.extend(k.ravel());elements.append((indices,k))
        # Trapezoidal external line-load quadrature: actual refinement retained.
        F[2*i]+=uniform_N_m*L/2;F[2*i+2]+=uniform_N_m*L/2
    for position,force in point_loads:
        if not 0<=position<=length_m:raise ValueError('Load outside physical beam')
        j=min(len(x)-2,max(0,int(np.searchsorted(x,position)-1)));r=(position-x[j])/(x[j+1]-x[j])
        F[2*j]+=force*(1-r);F[2*j+2]+=force*r
    for position,moment in point_moments:
        j=min(len(x)-2,max(0,int(np.searchsorted(x,position)-1)));q=(position-x[j])/(x[j+1]-x[j])
        F[2*j+1]+=moment*(1-q);F[2*j+3]+=moment*q
    springs={}
    for patch in bearing_patches:
        a,b,kn=patch['a_m'],patch['b_m'],patch['kn_N_m']
        if not b>a or kn<=0:raise ValueError('Finite positive sized bearing patch required')
        indices=np.flatnonzero((x>=a-1e-10)&(x<=b+1e-10));weights=[]
        for j in indices:
            low=max(a,(x[j-1]+x[j])/2 if j else a);high=min(b,(x[j]+x[j+1])/2 if j<len(x)-1 else b)
            weights.append(max(0.,high-low))
        total=sum(weights)
        for j,w in zip(indices,weights):springs[2*int(j)]=springs.get(2*int(j),0.)+kn*w/total
    for dof,kn in springs.items():rows.append(dof);cols.append(dof);values.append(kn)
    K=coo_matrix((values,(rows,cols)),shape=(size,size)).tocsc();fixed=[2*int(np.argmin(abs(x-p))) for p in supports]
    free=np.setdiff1d(np.arange(size),fixed);diagonal=K.diagonal()[free]
    if np.any(diagonal<=0):raise ValueError('Nonpositive unsupported structural DOF')
    scale=1/np.sqrt(diagonal);D=diags(scale);factor=splu((D@K[free][:,free]@D).tocsc());u=np.zeros(size);u[free]=scale*factor.solve(scale*F[free])
    R=K@u-F;res=float(np.linalg.norm(R[free])/max(1.,np.linalg.norm(F)));energy=float(u@(K@u)/2);work=float(u@F/2)
    bearing=[dict(position_m=float(x[d//2]),force_N=float(-kn*u[d])) for d,kn in sorted(springs.items())]
    support=[dict(position_m=float(x[d//2]),force_N=float(R[d])) for d in fixed]
    sum_force=float(F[::2].sum()+sum(p['force_N'] for p in bearing+support))
    sum_moment=float(np.dot(F[::2],x)+F[1::2].sum()+sum(p['force_N']*p['position_m'] for p in bearing+support))
    local=[k@u[index] for index,k in elements]
    maxmoment=max(max(abs(q[1]),abs(q[3])) for q in local);maxshear=max(max(abs(q[0]),abs(q[2])) for q in local)
    return dict(nodes_m=x.tolist(),deflections_m=u[::2].tolist(),rotations_rad=u[1::2].tolist(),
        maximum_deflection_m=float(abs(u[::2]).max()),maximum_rotation_rad=float(abs(u[1::2]).max()),
        maximum_bending_moment_Nm=float(maxmoment),maximum_shear_N=float(maxshear),bearing_reactions=bearing,support_reactions=support,
        free_relative_residual=res,strain_energy_J=energy,external_work_J=work,relative_energy_residual=abs(energy-work)/max(1.,abs(energy)),
        force_balance_residual_N=sum_force,moment_balance_residual_Nm=sum_moment,
        numerical_valid=bool(res<1e-6 and abs(energy-work)/max(1.,abs(energy))<1e-6),
        small_displacement_model_suspect=bool(abs(u[1::2]).max()>.1 or abs(u[::2]).max()/length_m>.01),
        approved_deflection_limit_m=None,approved_strength_margin=None)


def benchmarks():
    """Independent Hexcel hand calculation plus finite-element mesh controls."""
    L,b,P,t,tc,E,Gc=2.,.5,1500.,.0005,.0254,70e9,220e6;h=tc+t
    # Match published simplified D/S precisely, not a changed model against its rounded output.
    D=E*t*h*h*b/2;S=b*h*Gc
    analytical=P*L**3/(48*D)+P*L/(4*S)
    runs=[]
    for n in (8,16):
        r=beam_response(L,D,S,[(L/2,-P)],supports=(0.,L),divisions=n)
        runs.append(dict(divisions=n,computed_m=r['maximum_deflection_m'],relative_error=abs(r['maximum_deflection_m']-analytical)/analytical,
                         numerical_valid=r['numerical_valid']))
    exact=layered_section([dict(z_m=-h/2,thickness_m=t,E_Pa=E),dict(z_m=h/2,thickness_m=t,E_Pa=E)],tc,b,Gc)
    return dict(source_id='hexcel-sandwich',printed_pages=[12,13],published_rounded_deflection_m=.043,
        independent_analytical_deflection_m=analytical,published_bending_stiffness_Nm2=5869.6,computed_simplified_D_Nm2=D,
        computed_simplified_S_N=S,finite_element_runs=runs,layer_integration_EI_Nm2=exact['EI_Nm2'],
        layer_energy_shear_stiffness_N=exact['core_shear_stiffness_N'],
        benchmark_pass=all(x['relative_error']<1e-8 and x['numerical_valid'] for x in runs),
        scope='Published mathematical worked example, not physical rail/material/connection correlation')


def _rows(vehicle):
    registry=_vehicle(vehicle);parts={p['physical_definition_id']:p for p in registry['parts']};materials={m['material_id']:m for m in registry['materials']};rows=[]
    for o in registry['occurrences']:
        if not o['occurrence_id'].startswith('car-1/'):continue
        p=parts[o['part_definition_id']];T=np.asarray(o['transform'],dtype=float);g=p['geometry'];row=dict(occurrence=o,part=p,position=T[:3,3],rotation=T[:3,:3],grade=None)
        if p['material_id'] is not None:row['grade']=materials[p['material_id']]['grade_id']
        if g['kind'] in ('box','envelope'):
            d=np.asarray(g['dimensions_m']);extent=np.abs(T[:3,:3])@d;row.update(dimensions=d,lower=T[:3,3]-extent/2,upper=T[:3,3]+extent/2)
        rows.append(row)
    return rows


def _is(row,name):return row['occurrence']['occurrence_id'].split('/')[1]==name


def _face_E(row,hypothesis):
    if row['grade'].startswith('AL-'):return 70e9,'hulamin-6082-typical'
    if row['grade'].startswith('GFRP'):return hypothesis*1e9,'explicit-generic-candidate-laminate-hypothesis-not-qualified'
    raise ValueError('Unsupported face grade; no automatic material substitution')


def inventory(vehicle,face_E_GPa_hypothesis=20.,core_direction='unoriented-worst'):
    rows=_rows(vehicle);panels=[]
    Gc=18e6 if core_direction=='0deg' else 16e6
    for core in [r for r in rows if _is(r,'floor-core') or _is(r,'roof-core')]:
        roof=_is(core,'roof-core');name='roof' if roof else 'floor';x=float(core['position'][0]);tc=float(core['dimensions'][2]);b=float(core['dimensions'][1]);L=float(core['dimensions'][0])
        faces=[r for r in rows if _is(r,name+'-face') and abs(r['position'][0]-x)<1e-7]
        if len(faces)!=2 or core['grade']!='PET-KERDYN-80':raise ValueError('Actual two-face Kerdyn80 stack required')
        fs=[]
        for face in faces:
            E,basis=_face_E(face,face_E_GPa_hypothesis);fs.append(dict(z_m=float(face['position'][2]),thickness_m=float(face['dimensions'][2]),E_Pa=E,basis=basis))
        section=layered_section(fs,tc,b,Gc)
        ribs=[r for r in rows if _is(r,'roof-transverse-rib' if roof else 'transverse-floor-member')
              and core['lower'][0]<r['position'][0]<core['upper'][0]]
        patches=[]
        lowface=min(faces,key=lambda f:f['position'][2])
        for rib in ribs:
            lo=max(float(core['lower'][0]),float(rib['lower'][0]));hi=min(float(core['upper'][0]),float(rib['upper'][0]));width=max(0.,min(float(core['upper'][1]),float(rib['upper'][1]))-max(float(core['lower'][1]),float(rib['lower'][1])))
            area=(hi-lo)*width
            patches.append(dict(source_occurrence_id=rib['occurrence']['occurrence_id'],a_m=lo-float(core['lower'][0]),b_m=hi-float(core['lower'][0]),
                width_m=width,area_m2=area,kn_N_m=74e6*area/tc,
                actual_vertical_gap_m=float(lowface['lower'][2]-rib['upper'][2]),
                conditional_bearing_basis='Finite core flatwise compression stiffness Ez*A/tc, only if a load-transfer connection is manufactured',connection_defined=False))
        bonds=[r for r in rows if (_is(r,name+'-bondline') or r['occurrence']['occurrence_id'].split('/')[1].startswith(name+'-face-core-bond-')) and abs(r['position'][0]-x)<1e-7]
        bondaudit=[]
        for face in faces:
            interface=float(face['lower'][2]) if face['position'][2]>core['position'][2] else float(face['upper'][2])
            adjacent=[r for r in bonds if abs(r['position'][2]-interface)<=float(r['dimensions'][2])/2+1e-8]
            fits=bool(adjacent) and all(min(float(face['upper'][2]),float(b['upper'][2]))-max(float(face['lower'][2]),float(b['lower'][2]))<1e-8 for b in adjacent)
            bondaudit.append(dict(face_occurrence_id=face['occurrence']['occurrence_id'],interface_z_m=interface,
                counted_bond_occurrences=[r['occurrence']['occurrence_id'] for r in adjacent],
                finite_bond_thickness_fits_without_solid_overlap=fits,
                adhesive_shear_modulus_Pa=None,adhesive_shear_allowable_Pa=None,
                status='counted-net-bond-layer-needs-material-and-cure-qualification' if fits else 'counted-layer-overlap-needs-net-geometry-revision' if adjacent else 'missing-counted-bond-layer'))
        for patch in patches:
            rib=next(r for r in rows if r['occurrence']['occurrence_id']==patch['source_occurrence_id'])
            top=float(rib['upper'][2]);bottom=float(lowface['lower'][2]);segments=[];binding=[];compliance=tc/(74e6*patch['area_m2'])
            for row in rows:
                local=row['occurrence']['occurrence_id'].split('/')[1]
                if not local.startswith(name+'-rib-cap-') or 'lower' not in row:continue
                overlapx=min(float(row['upper'][0]),float(rib['upper'][0]))-max(float(row['lower'][0]),float(rib['lower'][0]))
                if overlapx<=1e-8 or abs(row['position'][1])>1e-8:continue
                segments.append((float(row['lower'][2]),float(row['upper'][2])));binding.append(row['occurrence']['occurrence_id'])
                E=70e9 if row['grade'].startswith('AL-') else 1e9
                compliance+=float(row['dimensions'][2])/(E*patch['area_m2'])
            frontier=top
            for a,b in sorted(segments):
                if a<=frontier+1e-8:frontier=max(frontier,b)
            patch['unfilled_gap_m']=max(0.,bottom-frontier);patch['counted_support_stack']=binding
            patch['connection_defined']=patch['unfilled_gap_m']<1e-8 and bool(binding)
            patch['kn_N_m']=1/compliance
            patch['adhesive_compressive_E_Pa_hypothesis']=1e9 if binding else None
        panels.append(dict(panel_id=core['occurrence']['occurrence_id'],kind=name,length_m=L,width_m=b,core_thickness_m=tc,
            origin_x_m=float(core['lower'][0]),centre_m=core['position'].tolist(),core_G_Pa=Gc,core_orientation=core_direction,
            actual_source_occurrences=[core['occurrence']['occurrence_id']]+[r['occurrence']['occurrence_id'] for r in faces+bonds],
            section=section,faces=fs,bearing_patches=patches,bond_audit=bondaudit,
            measured_material_or_joint_qualification=False))
    if len(panels)!=8:raise ValueError('Exactly four actual floor and four roof cassettes required')
    return rows,panels


def revision(vehicle,root=ROOT,bond_thickness_m=.0006):
    """Proposed *physical* revision: counted face bonds and finite support caps.

    No geometry is moved silently: two skins are separated for two adhesive
    layers, old one-sided overlapping bonds are replaced, and each actual rib
    gap receives an aluminium cap with two counted finite adhesive interfaces.
    Adhesive, net hole detail, cure, peel/fatigue/fire and load tests stay open.
    """
    from engineering.component_registry import make_part,make_occurrence,make_registry,summary
    from engineering.component_registry.materials import catalogue
    from engineering.reference_cell.vehicles import _mass_properties
    if not .0003<=bond_thickness_m<=.0012:raise ValueError('Explicit manufacturable bondline hypothesis .3..1.2mm required')
    rows,panels=inventory(vehicle);materials={m['grade_id']:m for m in catalogue()['materials']};parts={p['physical_definition_id']:deepcopy(p) for p in vehicle['registry']['parts']}
    remove=set();moves={};newlocal=[];log=[]
    for panel in panels:
        centre=panel['centre_m'];tc=panel['core_thickness_m'];name=panel['kind'];L=panel['length_m'];b=panel['width_m'];corez=centre[2]
        for row in rows:
            oid=row['occurrence']['occurrence_id']
            if abs(row['position'][0]-centre[0])>1e-7:continue
            if _is(row,name+'-bondline'):remove.add(oid.split('/',1)[1])
            if _is(row,name+'-face'):
                sign=1 if row['position'][2]>corez else -1
                position=row['position'].copy();position[2]=corez+sign*(tc/2+bond_thickness_m+row['dimensions'][2]/2)
                moves[oid.split('/',1)[1]]=position.tolist()
        for sign in (-1,1):newlocal.append((name+'-face-core-bond-'+panel['panel_id'].split('/')[-1]+'-'+str(sign),[L,b,bond_thickness_m],
            [centre[0],centre[1],corez+sign*(tc/2+bond_thickness_m/2)],'ADHESIVE-EPOXY-HYPOTHESIS','meter-mix-bond-controlled-cure-inspect'))
        for n,patch in enumerate(panel['bearing_patches']):
            rib=next(r for r in rows if r['occurrence']['occurrence_id']==patch['source_occurrence_id'])
            faces=[r for r in rows if _is(r,name+'-face') and abs(r['position'][0]-centre[0])<1e-7]
            lower=min(faces,key=lambda r:r['position'][2]);bottom=corez-tc/2-bond_thickness_m-float(lower['dimensions'][2])
            top=float(rib['upper'][2]);gap=bottom-top
            if gap<=2*bond_thickness_m:raise ValueError('No positive physical support-cap thickness remains')
            x=panel['origin_x_m']+(patch['a_m']+patch['b_m'])/2;dx=patch['b_m']-patch['a_m'];width=patch['width_m']
            capname=name+'-rib-cap-'+panel['panel_id'].split('/')[-1]+'-'+str(n)
            newlocal.append((capname,[dx,width,gap-2*bond_thickness_m],[x,0.,(bottom+top)/2],'AL-6082-T6-EXTRUSION','machine-fit-bond-inspect'))
            for sign in (-1,1):newlocal.append((capname+'-bond-'+str(sign),[dx,width,bond_thickness_m],
                [x,0.,top+bond_thickness_m/2 if sign<0 else bottom-bond_thickness_m/2],'ADHESIVE-EPOXY-HYPOTHESIS','meter-mix-bond-controlled-cure-inspect'))
            log.append(dict(panel=panel['panel_id'],rib=patch['source_occurrence_id'],original_gap_m=patch['actual_vertical_gap_m'],
                revised_gap_to_fill_m=gap,cap_net_thickness_m=gap-2*bond_thickness_m,bond_thickness_each_m=bond_thickness_m,
                footprint_m=[dx,width],new_module_name=capname,structural_qualified=False))
    added=[]
    for name,dims,pos,grade,process in newlocal:
        m=materials[grade];V=float(np.prod(dims));rho=m['density_kg_m3']
        p=make_part('OSR-'+vehicle['vehicle_id']+'-'+name.upper(),'A',['primary-body'],
            dict(kind='box',dimensions_m=dims,net_volume_m3=V),m['material_id'],
            dict(calculated_kg=V*rho['nominal'],lower_bound_kg=V*rho['lower'],upper_bound_kg=V*rho['upper'],evidence_state='calculated'),
            dict(method=process,process=process,cycle_hours=None,gross_to_net_yield_hypothesis=None,qualified_tooling=None),
            assembly=dict(attachment='finite-area bonded support or face/core layer',mating_parts_defined=True,
                approved_joint_allowable_Pa=None,adhesive_grade_and_cure_unresolved=True,fasteners_required_for_qualified_fail_safe_retention=None,
                removal='Support cassette, isolate/remove equipment, release bonded cap interfaces using controlled cut; damage inspection and rebond procedure required'),
            evidence=dict(state='physical-design-hypothesis',physical_test_ids=[],source=PRODUCER),
            lifecycle=dict(inspection_interval=None,repair_procedure=None,replacement_requires_bond_requalification=True))
        parts[p['physical_definition_id']]=p;added.append((name,p,pos))
    occ=[]
    for o in vehicle['registry']['occurrences']:
        local=o['occurrence_id'].split('/',1)[1]
        if local in remove:continue
        value=deepcopy(o);car=int(value['occurrence_id'].split('/')[0].split('-')[-1]);offset=17.5*(car-1)
        if local in moves:
            value['transform'][0][3]=moves[local][0]+offset;value['transform'][1][3]=moves[local][1];value['transform'][2][3]=moves[local][2]
        occ.append(value)
    for car in range(1,7):
        for name,p,pos in added:
            T=np.eye(4);T[:3,3]=[pos[0]+17.5*(car-1),pos[1],pos[2]]
            occ.append(make_occurrence('car-'+str(car)+'/'+name,p,parent_id='car-'+str(car)+'/primary-body',transform=T.tolist(),scope='vehicle/primary-body'))
    # Drop definitions no longer occurring; no ghost mass accounts.
    used={o['part_definition_id'] for o in occ};partlist=[p for k,p in parts.items() if k in used]
    reg=make_registry(vehicle['label']+'; counted sandwich support-cap revision',partlist,occ,vehicle['functional_requirements'],
        parent_candidate_id=vehicle['candidate_id'],assemblies=deepcopy(vehicle['registry']['assemblies']))
    result=deepcopy(vehicle);result.pop('evaluation_id',None);result['registry']=reg;result['candidate_id']=reg['candidate_id'];result['summary']=summary(reg)
    def massrows(onlycar):
        output=[];mapping={p['physical_definition_id']:p for p in reg['parts']}
        for o in reg['occurrences']:
            if onlycar and not o['occurrence_id'].startswith('car-1/'):continue
            T=np.asarray(o['transform']);axis='z'
            if abs(T[0,2])>.9:axis='x'
            elif abs(T[1,2])>.9:axis='y'
            output.append(dict(part=mapping[o['part_definition_id']],xyz=T[:3,3].tolist(),axis=axis))
        return output
    local=massrows(True);result['per_car_mass_properties']=_mass_properties(local);result['train_mass_properties']=_mass_properties(massrows(False))
    result['per_car_occurrences']=len(local);result['per_car_part_definitions']=len(partlist)
    result['per_car_functional_occurrences']={f:sum(f in p['part']['functions'] for p in local) for f in result['functional_requirements']}
    result['label']+='; counted sandwich support-cap revision'
    result['revision_ancestry']=dict(parent_candidate_id=vehicle['candidate_id'],parent_vehicle_evaluation_id=vehicle['evaluation_id'],
        reason='Replace one-sided overlapping face bonds and unfilled actual rib/skin gaps with counted finite geometry',
        changes=log,bond_thickness_m=bond_thickness_m,added_occurrences_per_car=len(added),removed_bond_occurrences_per_car=len(remove),
        mass_upper_delta_per_car_kg=result['per_car_mass_properties']['mass_upper_bound_kg']-vehicle['per_car_mass_properties']['mass_upper_bound_kg'])
    result['manufacturing_plan']=[dict(part_definition_id=p['physical_definition_id'],part_revision_id=p['revision_id'],part_id=p['part_id'],
        process=p['manufacturing'],required_inspections=['dimensional','material-lot','bondline-thickness','cure','adhesion','damage'],approved_work_instruction=None,qualified_tooling=None) for p in partlist]
    result['source_sha256']=sources(vehicle,root);result['geometry_scope']+='; finite net support caps and separate two-sided adhesive layers, unqualified bond/cure/repair interfaces'
    result['unresolved'].extend(['Support-cap peel/shear/fatigue/fire allowables and actual bonded-assembly tests','Qualified damage-tolerant retention and cassette removal/rebond method'])
    result['evaluation_id']=identity(result);_vehicle(result);return result


def _loading(vehicle,rows):
    bound=fsum(r['part']['mass']['upper_bound_kg'] for r in rows)
    bindings=[dict(occurrence_id=r['occurrence']['occurrence_id'],mass_upper_kg=r['part']['mass']['upper_bound_kg'],position_m=r['position'].tolist(),
        envelope_internal_CG_known=r['part']['geometry']['kind']!='envelope') for r in rows]
    equipment=[r for r in rows if 'running-gear' not in r['part']['functions']]
    seats=[r['position'] for r in rows if _is(r,'seat-pan')]
    for r in rows:
        if _is(r,'two-place-wall-bench'):seats.extend([r['position']+[-.24,0.,0.],r['position']+[.24,0.,0.]])
    seats.extend(np.asarray(p['center_m']) for p in vehicle['interfaces']['wheelchair_spaces_per_car'])
    if len(seats)!=46:raise ValueError('Actual44seats+2wheelchair positions required')
    normal=[(float(p[0]),75*G) for p in seats];crowd=[(float(x),750*G) for x in np.linspace(.5,16.5,16)]
    empty=[(float(r['position'][0]),r['part']['mass']['upper_bound_kg']*G) for r in equipment]
    return dict(empty=empty,normal=empty+normal,crowd160=empty+crowd),dict(total_car_upper_mass_kg=bound,
        supported_body_and_equipment_upper_mass_kg=fsum(r['part']['mass']['upper_bound_kg'] for r in equipment),
        excluded_directly_supported_running_gear_upper_mass_kg=bound-fsum(r['part']['mass']['upper_bound_kg'] for r in equipment),
        occurrence_mass_bindings=bindings,passenger_mass_kg=75.,normal_people=46,crowd_people=160,
        scope='All bounded masses reconciled; running gear supported directly at rails; purchased internal CG still unknown')


def _underframe(rows,load,divisions,face_E_GPa_hypothesis=20.):
    beams=[r for r in rows if _is(r,'underframe-web') or _is(r,'underframe-flange')]
    if len(beams)!=6:raise ValueError('Actual two three-part underframe I-sections required')
    zneutral=fsum(_face_E(r,face_E_GPa_hypothesis)[0]*float(r['dimensions'][1]*r['dimensions'][2])*float(r['position'][2]) for r in beams)/fsum(_face_E(r,face_E_GPa_hypothesis)[0]*float(r['dimensions'][1]*r['dimensions'][2]) for r in beams)
    EI=fsum(_face_E(r,face_E_GPa_hypothesis)[0]*float(r['dimensions'][1])*(float(r['dimensions'][2])**3/12+float(r['dimensions'][2])*(float(r['position'][2])-zneutral)**2) for r in beams)
    # GFRP rail cases remain separately hypothetical, never isotropic copper/core.
    webs=[r for r in beams if _is(r,'underframe-web')]
    S=fsum((26e9 if r['grade'].startswith('AL-') else 4e9)*float(r['dimensions'][1]*r['dimensions'][2]) for r in webs)
    start=max(float(r['lower'][0]) for r in beams);end=min(float(r['upper'][0]) for r in beams)
    projected=[];outside=[];moments=[]
    for x,F in load:
        if not start<=x<=end:
            M=-F*(x-min(end,max(start,x)));outside.append(dict(original_x_m=x,endpoint_moment_Nm=M));moments.append((min(end,max(start,x))-start,M))
        projected.append((min(end,max(start,x))-start,-F))
    result=beam_response(end-start,EI,S,projected,supports=(2.9-start,14.1-start),divisions=divisions,point_moments=moments)
    return dict(EI_Nm2=EI,shear_stiffness_N=S,neutral_axis_m=zneutral,source_occurrences=[r['occurrence']['occurrence_id'] for r in beams],response=result,
        unsupported_end_load_offsets=outside,endpoint_moments_not_applied=False,
        scope='Two actual underframe rails share vertical loads as a conditional necessary-demand model; no claim of real transverse joints or full-body shell stiffness',
        load_transfer_connection_qualified=False)


def evaluate(vehicle,*,root=ROOT,**options):
    r=request(vehicle,root=root,**options);rows,panels=inventory(vehicle,r['face_E_GPa_hypothesis'],r['core_direction']);loads,mass=_loading(vehicle,rows)
    results=[]
    for divisions in r['divisions']:
        current=[]
        for panel in panels:
            p=deepcopy(panel);section=p['section'];a=p['origin_x_m'];L=p['length_m'];cases=[]
            for name,load in loads.items():
                applicable=[]
                for x,F in load:
                    if a<=x<=a+L:
                        # Roof carries only its located roof/HVAC/solar equipment; floor conservative remainder.
                        applicable.append((x-a,-F))
                if p['kind']=='roof':
                    applicable=[(float(row['position'][0])-a,-row['part']['mass']['upper_bound_kg']*G) for row in rows
                        if a<=row['position'][0]<=a+L and (row['position'][2]>3.4 or _is(row,'roof-core'))]
                response=beam_response(L,section['EI_Nm2'],section['core_shear_stiffness_N'],applicable,
                    bearing_patches=p['bearing_patches'],divisions=divisions)
                h=section['face_centre_separation_m'];face_stress=max(response['maximum_bending_moment_Nm']/(p['width_m']*h*f['thickness_m']) for f in p['faces'])
                cases.append(dict(load_case=name,response=response,face_normal_stress_proxy_Pa=face_stress,
                    core_shear_stress_proxy_Pa=response['maximum_shear_N']/(p['width_m']*h),
                    core_typical_shear_strength_Pa=580000.,typical_strength_is_design_allowable=False,
                    approved_face_margin=None,approved_core_margin=None,approved_bond_margin=None))
            current.append(dict(panel=p,cases=cases))
        results.append(dict(divisions=divisions,panels=current,underframe_cases=[dict(load_case=name,**_underframe(rows,load,divisions,r['face_E_GPa_hypothesis'])) for name,load in loads.items()]))
    refinement=[]
    for p,q in zip(results[0]['panels'],results[1]['panels']):
        refinement.extend(dict(panel_id=p['panel']['panel_id'],load_case=a['load_case'],coarse_deflection_m=a['response']['maximum_deflection_m'],
            fine_deflection_m=b['response']['maximum_deflection_m'],relative_change=abs(a['response']['maximum_deflection_m']-b['response']['maximum_deflection_m'])/max(1e-20,b['response']['maximum_deflection_m'])) for a,b in zip(p['cases'],q['cases']))
    missing=[dict(panel_id=p['panel_id'],source_occurrence_id=patch['source_occurrence_id'],gap_m=patch['actual_vertical_gap_m'])
        for p in panels for patch in p['bearing_patches'] if patch['unfilled_gap_m']>1e-6]
    value=dict(schema='osr-layered-structure-evaluation/1',candidate_id=vehicle['candidate_id'],vehicle_evaluation_id=vehicle['evaluation_id'],
        request_id=r['request_id'],execution='completed-conditional-calculations',mass=mass,results=results,refinement=refinement,
        primary_sources=primary_sources(root),method_benchmark=benchmarks(),source_sha256=r['source_sha256'],
        unfilled_support_interface_gaps=missing,whole_body_coupled_solution_completed=False,
        engineering_screen='conditional-local-panel-and-underframe-results; actual-bonds-and-full-body-load-path-review-required',
        diagnosis=['Separate face/core bending misses the parallel-axis face couple; these layered sections explicitly include it',
            'Core shear uses Kerdyn80 manufacturer16/18MPa, not the old wrong-grade25MPa hypothesis',
            'Skin/core compatibility assumes perfect transfer only within each conditional local panel; no infinite inter-part joint is inserted',
            'Actual finite rib footprints are retained, but empty gaps/one-sided overlapping bonds are definition defects, not material failure'],
        revision_requests=['Count two finite face-core adhesive layers and correct skin separation before claiming a buildable sandwich',
            'Define/count finite ribs-to-skin caps and bonded/fastened load-transfer details at every listed gap',
            'Provide actual laminate, adhesive/cure/hot-wet/peel/fatigue/fire records and test local bearing/indentation and full-body coupling'],
        approved_strength_allowables=None,actual_laminate_schedule=None,hot_wet_retention=None,
        limitations=['One-dimensional shear-flexible strip per whole-width cassette; torsion and plate transverse redistribution unrepresented',
            'No qualified shell buckling, wrinkling, peel, load-introduction fatigue, crash or installed-assembly acceptance',
            'Necessary underframe response does not sum with panel maxima into a manufactured whole-body result',
            'No L/500 universal rejection; functional door/glazing/air-gap limits require their actual approved interfaces'],**FLAGS)
    value['evaluation_id']=identity(value);return value


def run(value,output,*,root=ROOT):
    """One bounded subprocess; retains source/input/logs and failures unchanged."""
    _validate_request(value,root);folder=Path(output).resolve()
    if folder.exists():raise ValueError('Fresh private numerical folder required')
    folder.mkdir(parents=True);(folder/'input.json').write_bytes(encoded(value))
    with tarfile.open(folder/'sources.tar','w') as archive:
        for name,expected in value['source_sha256'].items():
            data=(Path(root)/name).read_bytes()
            if sha256(data).hexdigest()!=expected:raise ValueError('Source changed before worker')
            item=tarfile.TarInfo(name);item.size=len(data);item.mode=0o444;archive.addfile(item,io.BytesIO(data))
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    script='from engineering.sourced_case.structure import _worker; _worker('+repr(str(folder))+','+repr(str(Path(root).resolve()))+')'
    started=time.monotonic();out=b'';err=b'';code=None;failure=None
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(value['memory_bytes'],value['memory_bytes']))
        resource.setrlimit(resource.RLIMIT_CPU,(value['maximum_seconds'],value['maximum_seconds']+1))
    try:
        p=subprocess.run([sys.executable,'-c',script],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=value['maximum_seconds'],preexec_fn=limits);out,err,code=p.stdout,p.stderr,p.returncode
        if code:failure='Worker exited '+str(code)
    except subprocess.TimeoutExpired as error:out=error.stdout or b'';err=error.stderr or b'';failure='Worker timeout'
    (folder/'stdout.log').write_bytes(out);(folder/'stderr.log').write_bytes(err)
    if not (folder/'result.json').exists():
        (folder/'result.json').write_bytes(encoded(dict(schema='osr-layered-structure-failed/1',request_id=value['request_id'],
            candidate_id=value['candidate_id'],execution='failed',reason=failure or 'No numerical output',**FLAGS)))
    report=dict(schema='osr-layered-structure-package/1',request_id=value['request_id'],candidate_id=value['candidate_id'],
        source_sha256=value['source_sha256'],returncode=code,failure=failure,elapsed_s=time.monotonic()-started,
        actual_resource_limits=dict(address_space_bytes=value['memory_bytes'],wall_timeout_s=value['maximum_seconds']),
        execution_isolation='Ordinary child process with RLIMIT_AS/RLIMIT_CPU and wall timeout; filesystem/network are not sandboxed',
        python_version=sys.version,python_sha256=digest(sys.executable),numpy_version=np.__version__,
        files={p.name:dict(sha256=digest(p),bytes=p.stat().st_size) for p in folder.iterdir() if p.is_file()},**FLAGS)
    report['package_id']=identity(report);(folder/'manifest.json').write_bytes(encoded(report));return report


def _worker(folder,root):
    path=Path(folder);r=json.loads((path/'input.json').read_text());_validate_request(r,root)
    result=evaluate(r['vehicle'],root=root,divisions=r['divisions'][0],face_E_GPa_hypothesis=r['face_E_GPa_hypothesis'],
        core_direction=r['core_direction'],maximum_seconds=r['maximum_seconds'],memory_bytes=r['memory_bytes'])
    (path/'result.json').write_bytes(encoded(result))


def verify(output,*,root=ROOT,require_current_source=True,recompute=False):
    """Strict recorded package verification; optional independent numerical replay.

    Default does not pretend to replay archived code with current tools. A new
    numerical replay is root-budgeted separately. All archive members are read
    in memory, never extracted; symlinks, duplicates, traversal are refused.
    """
    folder=Path(output)
    if {p.name for p in folder.iterdir()}!=FILES:raise ValueError('Closed structural package inventory differs')
    manifest=json.loads((folder/'manifest.json').read_text())
    if manifest.get('package_id')!=identity({k:v for k,v in manifest.items() if k!='package_id'}):raise ValueError('Structural package identity differs')
    if set(manifest['files'])!=FILES-{'manifest.json'}:raise ValueError('Payload inventory differs')
    for name,row in manifest['files'].items():
        path=folder/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size!=row['bytes'] or digest(path)!=row['sha256']:raise ValueError('Structural payload differs: '+name)
    if (folder/'sources.tar').stat().st_size>256*1024**2:raise ValueError('Source archive resource bound exceeded')
    with tarfile.open(folder/'sources.tar') as archive:
        members=archive.getmembers();names=[m.name for m in members]
        if len(names)!=len(set(names)) or set(names)!=set(manifest['source_sha256']):raise ValueError('Source archive inventory differs')
        total=0
        for member in members:
            if not member.isfile() or member.name.startswith('/') or '..' in PurePosixPath(member.name).parts or '\\' in member.name:raise ValueError('Ordinary relative source files required')
            total+=member.size
            if member.size>32*1024**2 or total>256*1024**2:raise ValueError('Bounded source extraction required')
            data=archive.extractfile(member).read()
            if sha256(data).hexdigest()!=manifest['source_sha256'][member.name]:raise ValueError('Archived source hash differs')
    r=json.loads((folder/'input.json').read_text());result=json.loads((folder/'result.json').read_text())
    if r['request_id']!=identity({k:v for k,v in r.items() if k!='request_id'}) or r['request_id']!=manifest['request_id'] or r['candidate_id']!=manifest['candidate_id']:raise ValueError('Recorded request identity differs')
    _vehicle(r['vehicle'])
    if r['source_sha256']!=manifest['source_sha256'] or r['vehicle_evaluation_id']!=r['vehicle']['evaluation_id']:raise ValueError('Source/vehicle evaluation differs')
    if any(manifest.get(k) is not False or result.get(k) is not False for k in FLAGS):raise ValueError('Recorded package cannot confer acceptance')
    if require_current_source:_validate_request(r,root)
    if result['request_id']!=r['request_id'] or result['candidate_id']!=r['candidate_id']:raise ValueError('Numerical output belongs to another candidate/request')
    if result['execution']=='completed-conditional-calculations':
        if result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Evaluation identity differs')
        if result['vehicle_evaluation_id']!=r['vehicle_evaluation_id'] or result['source_sha256']!=r['source_sha256']:raise ValueError('Evaluation input differs')
        if not result['method_benchmark']['benchmark_pass']:raise ValueError('Published independent benchmark failed')
        if recompute:
            fresh=evaluate(r['vehicle'],root=root,divisions=r['divisions'][0],face_E_GPa_hypothesis=r['face_E_GPa_hypothesis'],core_direction=r['core_direction'],
                maximum_seconds=r['maximum_seconds'],memory_bytes=r['memory_bytes'])
            # Recorded source/tool replay remains explicit; floating algebra never changes the stored evaluation.
            for actual,saved in zip(fresh['refinement'],result['refinement']):
                if actual['panel_id']!=saved['panel_id'] or actual['load_case']!=saved['load_case'] or not np.isclose(actual['fine_deflection_m'],saved['fine_deflection_m'],rtol=1e-8,atol=1e-12):raise ValueError('Independent panel recomputation differs')
    elif result['execution']!='failed':raise ValueError('Unknown execution state')
    report=dict(package_id=manifest['package_id'],candidate_id=manifest['candidate_id'],evaluation_id=result.get('evaluation_id'),execution=result['execution'],
        recorded_source_payload_verified=True,current_source_verified=require_current_source,current_numerical_recomputed=recompute,
        full_body_or_physical_acceptance=False,**FLAGS)
    report['verification_id']=identity(report);return report
