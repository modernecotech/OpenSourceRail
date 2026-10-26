"""Candidate-specific wheel-car body iterations and bounded native screens.

Physical stock is independent of numerical constants. Side participation is a
synthetic balanced-crossply continuum with ideal intact clamp pads: useful for
investigating load paths, never a qualified laminate, bolted joint or whole car.
The trusted frozen C3D20 frame producer supplies actual tube walls and supports.
"""
from copy import deepcopy
from math import ceil,pi,prod,isfinite
from pathlib import Path
import json,os,re,subprocess,time,resource
from engineering.station_rail import ROOT,FLAGS,body_frame,body_floor_fit,body_solid_frame
from engineering.station_rail.common import encoded,identity,digest
from engineering.station_rail.vehicle import box,cylinder,tube

PRODUCER='engineering/design_search/wheel_body.py'
_Q11=25e9/(1-.25*.25*8/25);_Q22=8e9/(1-.25*.25*8/25);_Q12=.25*8e9/(1-.25*.25*8/25)
_SKIN_Q=(_Q11+_Q22)/2;SKIN_E=_SKIN_Q-_Q12**2/_SKIN_Q;SKIN_NU=_Q12/_SKIN_Q
CONSTITUTIVE=dict(skin_model='Balanced [0/90/90/0] classical-laminate extensional homogenisation; through-thickness constants remain synthetic; no ply stress/failure claim',
    E_longitudinal_Pa=SKIN_E,E_vertical_Pa=SKIN_E,E_through_Pa=8e9,nu_inplane=SKIN_NU,G_inplane_Pa=4e9,G_through_Pa=3e9,
    foam_E_Pa=80e6,foam_nu=.25,bond_E_Pa=1.5e9,bond_nu=.30,
    provenance='Declared synthetic research constants; not supplier-certified or prototype-correlated',
    joint='Ideal intact clamps/bolts; rigid load-transfer pads at actual counted fasteners. Holes omitted from continuum stiffness, retained in physical material mass. No slip/preload/fatigue evidence.')


def default_parameters():
    return dict(family='frame_only',sill_depth_m=.35,sill_wall_m=.008,clamp_plate_thickness_m=.003)


def initial_parameters():
    a=default_parameters();b={**a,'family':'participating_sandwich'}
    return [a,b]


def _parameters(parameters):
    p=deepcopy(parameters)
    if set(p)!=set(default_parameters()):raise ValueError('Explicit bounded wheel body parameter keys required')
    if p['family'] not in ('frame_only','participating_sandwich'):raise ValueError('Unknown body family')
    if (p['sill_depth_m'],p['sill_wall_m']) not in ((.35,.008),(.60,.012),(.60,.016),(.65,.016)):raise ValueError('Outside counted sill family')
    if p['clamp_plate_thickness_m'] not in (.003,.004):raise ValueError('Outside counted clamp family')
    return p


def revise(parameters,diagnostics,generation):
    p=_parameters(parameters)
    if generation<1:raise ValueError('Positive revision generation required')
    def failure(value):
        if isinstance(value,dict):
            for key,child in value.items():
                if key in ('maximum_vertical_displacement_m','normal_deflection_m') and isinstance(child,(int,float)) and child>.0256:return True
                if failure(child):return True
        elif isinstance(value,(list,tuple)):return any(failure(child) for child in value)
        elif isinstance(value,str):return value.lower() in ('fail','failed') or value.lower().startswith('failed-')
        return False
    failed=failure(diagnostics)
    if failed:
        sizes=[(.35,.008),(.60,.012),(.60,.016),(.65,.016)];i=sizes.index((p['sill_depth_m'],p['sill_wall_m']))
        if i<len(sizes)-1:p['sill_depth_m'],p['sill_wall_m']=sizes[i+1]
    return p


def _pad_hardware(parts,thickness):
    members=body_frame.members_from_stock(parts);posts=[m for m in members if m['axis']==2 and m['id'].startswith('comfort-shell/replacement-frame/') and '-post-' in m['id']]
    extras=[];holes=[];pads=[]
    for i,m in enumerate(posts):
        side=1 if m['start_m'][1]>0 else -1;outer=side*1.325
        for end,z in enumerate((m['start_m'][2]+.04,m['end_m'][2]-.04)):
            x=m['start_m'][0];w=min(.08,max(p['at_m'][0]+p['size_m'][0] for p in m['stock'])-min(p['at_m'][0] for p in m['stock']))
            at=(x-w/2,outer if side>0 else outer-thickness,z-.04)
            plate=box(f'wheel-shell-clamp/{i}/{end}/plate',at,(w,thickness,.08),system='body-panel-connections');extras.append(plate)
            pad=dict(post_id=m['id'],end=end,side=side,x_m=x,z_m=z,reference_z_m=m['start_m'][2] if end==0 else m['end_m'][2],plate_id=plate['id'],bolt_axes=[])
            y0=min(p['at_m'][1] for p in m['stock']);y1=max(p['at_m'][1]+p['size_m'][1] for p in m['stock'])
            low=min(y0,at[1]);high=max(y1,at[1]+thickness)
            for bolt,xx in enumerate((x-w/4,x+w/4)):
                prefix=f'wheel-shell-clamp/{i}/{end}/bolt/{bolt}';lowrod=low-.0075;highrod=high+.0015
                extras.extend([cylinder(prefix+'/shank',(xx,lowrod,z),.004,highrod-lowrod),
                    cylinder(prefix+'/head',(xx,highrod,z),.007,.005),
                    cylinder(prefix+'/nut',(xx,low-.0075,z),.007,.006,inner=.004),
                    cylinder(prefix+'/washer-low',(xx,low-.0015,z),.009,.0015,inner=.0045),
                    cylinder(prefix+'/washer-high',(xx,high,z),.009,.0015,inner=.0045)])
                holes.append(dict(x_m=xx,z_m=z,y_low_m=low,y_high_m=high,radius_m=.0045));pad['bolt_axes'].append([xx,z])
            pads.append(pad)
    return extras,holes,pads


def _drill(parts,holes):
    changed=[];removed=0.
    for original in parts:
        p=deepcopy(original)
        if p.get('kind') not in ('box','box-with-rectangular-cutouts'):changed.append(p);continue
        cuts=[]
        for h in holes:
            x,z,r=h['x_m'],h['z_m'],h['radius_m']
            y0,y1=p['at_m'][1],p['at_m'][1]+p['size_m'][1]
            if y1<=h['y_low_m'] or y0>=h['y_high_m']:continue
            if not(p['at_m'][0]+r<x<p['at_m'][0]+p['size_m'][0]-r and p['at_m'][2]+r<z<p['at_m'][2]+p['size_m'][2]-r):continue
            if p.get('rectangular_cutouts'):raise ValueError('Panel fastener unexpectedly crosses an existing rectangular cutout')
            cuts.append(dict(axis='y',diameter_m=2*r,x_m=x-p['at_m'][0],z_m=z-p['at_m'][2],length_m=p['size_m'][1]))
        if cuts:
            removed_volume=sum(pi*(h['diameter_m']/2)**2*p['size_m'][1] for h in cuts)
            p['analysis_uncut_volume_m3']=p['volume_m3'];p['analysis_uncut_mass_kg']=p['mass_kg'];p['source_part_id']=p.get('source_part_id',p['id'])
            p['id']+='-drilled-'+identity(cuts)[:10];p['holes']=p.get('holes',[])+cuts;p['volume_m3']-=removed_volume;p['mass_kg']=p['volume_m3']*p['density_kg_m3'];removed+=removed_volume*p['density_kg_m3']
            p.pop('inertia_kg_m2',None);p['cg_m']=None;p['mass_properties_scope']='Drilled part CG/inertia not calculated; native CAD must derive them'
        changed.append(p)
    return changed,removed


def _physical_body_parts(parts):
    fields=('id','kind','at_m','size_m','axis','radius_m','inner_radius_m','length_m','holes','rectangular_cutouts',
        'volume_m3','mass_kg','density_kg_m3','material','system','role','laminate_specification','source_part_id')
    return [{key:deepcopy(p[key]) for key in fields if key in p} for p in parts
        if p.get('system') not in ('bogies','brake-housing-stock') and not p['id'].startswith('station-secondary/')]


def materialize(base_vehicle,parameters,root=ROOT):
    p=_parameters(parameters)
    if 'wheel_body' in base_vehicle:raise ValueError('Materialize from the explicit unchanged base, not an already revised child')
    v=deepcopy(base_vehicle);floor=body_floor_fit.build(base_vehicle,root)
    changed=floor['physical_definition']['geometry_parts'];replaced={r['parent_part_id'] for r in floor['physical_definition']['removed_stock']}
    parts=[deepcopy(q) for q in base_vehicle['geometry_parts'] if q['id'] not in replaced]+deepcopy(changed)
    # The new sill's upper face and lateral centrelines stay fixed.
    old=[m for m in body_frame.members_from_stock(parts) if m['id'].startswith('wheel-underframe/sill/')]
    if (p['sill_depth_m'],p['sill_wall_m'])!=(.35,.008):
        oldids={q['id'] for m in old for q in m['stock']};parts=[q for q in parts if q['id'] not in oldids]
        for i,m in enumerate(old):
            top=max(q['at_m'][2]+q['size_m'][2] for q in m['stock'])
            tube(parts,f'wheel-underframe/sill/body-revision/{i}',(m['start_m'][0],m['start_m'][1]-.09,top-p['sill_depth_m']),m['length_m'],.18,p['sill_depth_m'],p['sill_wall_m'])
    hardware=[];pads=[];removed_holes=0.
    if p['family']=='participating_sandwich':
        hardware,holes,pads=_pad_hardware(parts,p['clamp_plate_thickness_m']);parts.extend(hardware);parts,removed_holes=_drill(parts,holes)
        for q in parts:
            if q.get('role')=='panel-side' and q.get('density_kg_m3')==1900:
                q['source_part_id']=q.get('source_part_id',q['id']);q['id']+='-balanced-crossply';q['material']='proposed-E-glass-epoxy-balanced-crossply';q['laminate_specification']=dict(angles_deg=[0,90,90,0],total_thickness_m=.002)
    delta=sum(q['mass_kg'] for q in parts)-sum(q['mass_kg'] for q in base_vehicle['geometry_parts'])
    physical=dict(parent_candidate_id=base_vehicle['candidate_id'],parent_body_candidate_id=base_vehicle['body_candidate_id'],parameters=p,
        geometry_parts=_physical_body_parts(parts),support_interface_id=base_vehicle['support_component_id'])
    bodyid=identity(physical);candidate=identity(dict(parent_candidate_id=base_vehicle['candidate_id'],body_candidate_id=bodyid,support_component_id=v['support_component_id'],propulsion_component_id=v['propulsion_component_id']))
    v['candidate_id']=candidate;v['body_candidate_id']=bodyid;v['geometry_parts']=parts;v['body_physical_definition']=physical
    v['physical_definition']['body_revision']=dict(body_candidate_id=bodyid,parent_body_candidate_id=base_vehicle['body_candidate_id'],parameters=deepcopy(p))
    v['physical_definition']['geometry_definition_id']=identity(parts)
    for key in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):v['mass'][key]+=delta
    v['mass']['accounted_tare_kg_six_cars']=6*v['mass']['accounted_tare_kg_per_car'];v['mass']['located_material_kg']=sum(q['mass_kg'] for q in parts);v['mass']['located_material_CG_m']=None
    v['mass'].update(installed_tare_kg_per_car=None,installed_loaded_kg_per_car=None,CG_m=None,inertia_kg_m2=None)
    v['axle_loads'].update(empty_kg_per_axle=v['mass']['accounted_tare_kg_per_car']/4,normal_kg_per_axle=v['mass']['accounted_cap_loaded_kg_per_car']/4,crowd_control_kg_per_axle=v['mass']['accounted_160_control_kg_per_car']/4)
    for stale in ('underframe_screens','ideal_body_coupling_screens','secondary_connectivity','evaluation_id'):v.pop(stale,None)
    v['inventory'].append(dict(id='wheel-body-revision',system='body',evidence_class='exact-material-delta-with-unqualified-joints',mass_kg=delta))
    v['wheel_body']=dict(parameters=p,parent_candidate_id=base_vehicle['candidate_id'],stock_mass_delta_kg=delta,floor_fit_mass_delta_kg=floor['net_material_mass_delta_kg'],
        shell_hardware_mass_kg=sum(q['mass_kg'] for q in hardware),drilled_material_removed_kg=removed_holes,pads=pads,
        unknown_additional_hardware_mass_kg=None,installed_mass_complete=False,physical_accepted=False,
        part_graph=dict(parts=[dict(id=q['id'],source_part_id=q.get('source_part_id'),mass_kg=q['mass_kg'],material=q.get('material')) for q in parts],pad_connections=pads),
        lineage='Composed counted floor fit, optional replaced sills and optional counted side clamps; no inherited frame results')
    v['source_sha256']={**base_vehicle['source_sha256'],body_frame.PRODUCER:digest(Path(root)/body_frame.PRODUCER),body_floor_fit.PRODUCER:digest(Path(root)/body_floor_fit.PRODUCER),body_solid_frame.PRODUCER:digest(Path(root)/body_solid_frame.PRODUCER),PRODUCER:digest(__file__)}
    v.update(FLAGS);v['evaluation_id']=identity(v);return v


def _analysis_variant(vehicle):
    # Explicitly omit local drilled-hole stress effects from this global screen.
    parts=[]
    for q in vehicle['geometry_parts']:
        p=deepcopy(q)
        if 'analysis_uncut_volume_m3' in p:
            p['volume_m3']=p['analysis_uncut_volume_m3'];p['mass_kg']=p['analysis_uncut_mass_kg'];p['cg_m']=[p['at_m'][j]+p['size_m'][j]/2 for j in range(3)]
        parts.append(p)
    ms=body_frame.members_from_stock(parts);cs=body_frame.contacts(ms);comps=body_frame._components(ms,cs);lower=next(i for i,m in enumerate(ms) if m['id'].startswith('wheel-underframe/sill/'));supported=next(c for c in comps if lower in c)
    return dict(name='candidate-body',alternative_id=vehicle['body_candidate_id'],members=ms,contacts=cs,supported_member_indices=supported,
        disconnected_member_ids=[m['id'] for i,m in enumerate(ms) if i not in supported],added_mass_kg=0.)


def _parse_nodes(raw):
    nodes={};active=False
    for line in raw.splitlines():
        if line.upper()=='*NODE':active=True;continue
        if line.startswith('*'):active=False
        if active:
            f=line.split(',');nodes[int(f[0])]=list(map(float,f[1:4]))
    return nodes


def _sandwich(raw,variant,vehicle,dx):
    """Actual side rectangles + counted plates; ideal fastener pads to frame."""
    frame=body_frame._mesh(variant,dx);nbase=max(frame['nodes']);oldnodes=_parse_nodes(raw);nextnode=max(oldnodes);nextel=1000000
    parts=[q for q in vehicle['geometry_parts'] if q.get('role')=='panel-side' or q['id'].startswith('wheel-shell-clamp/') and '/plate' in q['id']]
    xs={x for q in parts for x in (q['at_m'][0],q['at_m'][0]+q['size_m'][0])};zs={z for q in parts for z in (q['at_m'][2],q['at_m'][2]+q['size_m'][2])}
    for pad in vehicle['wheel_body']['pads']:
        xs.update(x for x,z in pad['bolt_axes']);zs.update(z for x,z in pad['bolt_axes'])
    xs.update(-8.4543+i*16.9086/ceil(16.9086/dx) for i in range(ceil(16.9086/dx)+1));zs.update(1.001+i*2.7533/ceil(2.7533/dx) for i in range(ceil(2.7533/dx)+1))
    xs=sorted({round(x,10) for x in xs});zs=sorted({round(z,10) for z in zs});lookup={};nodes={};els=[];volume=0.
    def node(point):
        nonlocal nextnode
        key=tuple(round(x,10) for x in point)
        if key not in lookup:nextnode+=1;lookup[key]=nextnode;nodes[nextnode]=list(point)
        return lookup[key]
    edges=((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7))
    for p in parts:
        # Global structural stiffness uses uncut prisms; actual holes are counted
        # in physical CAD/BOM and remain a local stress/bearing verification hold.
        x0,y0,z0=p['at_m'];lx,ly,lz=p['size_m'];x1=x0+lx;z1=z0+lz
        xx=[x for x in xs if x0-1e-8<=x<=x1+1e-8];zz=[z for z in zs if z0-1e-8<=z<=z1+1e-8]
        material='SKIN' if p.get('density_kg_m3')==1900 else 'CORE' if p.get('density_kg_m3')==80 else 'AL' if p['id'].startswith('wheel-shell-clamp/') else 'BOND'
        for a,b in zip(xx,xx[1:]):
            for c,d in zip(zz,zz[1:]):
                points=[[a,y0,c],[b,y0,c],[b,y0+ly,c],[a,y0+ly,c],[a,y0,d],[b,y0,d],[b,y0+ly,d],[a,y0+ly,d]]
                points += [[(points[a][j]+points[b][j])/2 for j in range(3)] for a,b in edges]
                nextel+=1;els.append((nextel,material,[node(p) for p in points]));volume+=(b-a)*ly*(d-c)
    expected=sum(p.get('analysis_uncut_volume_m3',p['volume_m3']) for p in parts)
    if abs(volume-expected)>1e-7:raise ValueError('Sandwich region mesh does not match actual aperture stock')
    extra=['*NODE']+[str(k)+','+','.join(f'{x:.12g}' for x in p) for k,p in nodes.items()]
    groups={}
    for eid,mat,ids in els:groups.setdefault(mat,[]).append((eid,ids))
    for mat,group in groups.items():
        extra.append('*ELEMENT,TYPE=C3D20,ELSET=P_'+mat)
        for eid,ids in group:extra += [str(eid)+','+','.join(map(str,ids[:15]))+',',','.join(map(str,ids[15:]))]
    extra += ['*MATERIAL,NAME=SKIN','*ELASTIC,TYPE=ENGINEERING CONSTANTS',f'{SKIN_E},{SKIN_E},8e9,{SKIN_NU},.25,.25,4e9,3e9','3e9',
        '*ORIENTATION,NAME=SKIN_AXES','1.,0.,0.,0.,0.,1.','*MATERIAL,NAME=CORE','*ELASTIC',f"{CONSTITUTIVE['foam_E_Pa']},{CONSTITUTIVE['foam_nu']}",'*MATERIAL,NAME=BOND','*ELASTIC',f"{CONSTITUTIVE['bond_E_Pa']},{CONSTITUTIVE['bond_nu']}"]
    for mat in groups:extra += [f'*SOLID SECTION,ELSET=P_{mat},MATERIAL={mat}'+(',ORIENTATION=SKIN_AXES' if mat=='SKIN' else '')]
    masters={}
    for i,m in enumerate(variant['members']):
        if not m['id'].startswith('comfort-shell/replacement-frame/') or '-post-' not in m['id']:continue
        for end,z in enumerate((m['start_m'][2],m['end_m'][2])):
            candidates=[k for k,p in frame['nodes'].items() if abs(p[0]-m['start_m'][0])<1e-8 and abs(p[1]-m['start_m'][1])<1e-8 and abs(p[2]-z)<1e-8]
            if candidates:masters[m['id'],end]=min(candidates)
    equations=0
    for pad in vehicle['wheel_body']['pads']:
        master=masters[pad['post_id'],pad['end']];origin=frame['nodes'][master];rot=nbase+master
        outer=pad['side']*(1.325+vehicle['wheel_body']['parameters']['clamp_plate_thickness_m'])
        for x,z in pad['bolt_axes']:
            key=tuple(round(a,10) for a in (x,outer,z))
            if key not in lookup:raise ValueError('Actual counted clamp bolt axis absent from native surface mesh')
            child=lookup[key];r=[x-origin[0],outer-origin[1],z-origin[2]]
            cross={0:[(2,-r[2]),(3,r[1])],1:[(3,-r[0]),(1,r[2])],2:[(1,-r[1]),(2,r[0])]}
            for j in range(3):
                terms=[(child,j+1,1.),(master,j+1,-1.)]+[(rot,d,c) for d,c in cross[j] if abs(c)>1e-12]
                extra += ['*EQUATION',str(len(terms)),','.join(f'{n},{d},{c:.12g}' for n,d,c in terms)];equations+=1
    extra+=['*NSET,NSET=FRAME'];ids=sorted(nodes);extra += [','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]
    return raw.replace('*STEP','\n'.join(extra)+'\n*STEP',1),dict(side_solid_elements=len(els),side_nodes=len(nodes),meshed_uncut_stock_volume_m3=volume,
        actual_aperture_regions=len(parts),ideal_fastener_equations=equations,synthetic_materials=True,holes_resolved=False)


def _address_space_bound():
    inherited=resource.getrlimit(resource.RLIMIT_AS)
    return min([3*1024**3,*[limit for limit in inherited if limit!=resource.RLIM_INFINITY]])


def _memory_bound():
    # Respect stricter inherited limits; this is address space, not measured RSS.
    bound=_address_space_bound();resource.setrlimit(resource.RLIMIT_AS,(bound,bound))


def _native(raw,folder,timeout_s=150):
    folder.mkdir();(folder/'body.inp').write_text(raw);started=time.monotonic();bound=_address_space_bound()
    try:
        proc=subprocess.run(['/usr/bin/ccx','body'],cwd=folder,capture_output=True,text=True,timeout=timeout_s,preexec_fn=_memory_bound,env={**os.environ,'OMP_NUM_THREADS':'1'})
        (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
        if proc.returncode or not(folder/'body.dat').is_file():return dict(execution='tool_error',returncode=proc.returncode,runtime_s=time.monotonic()-started,address_space_limit_bytes=bound)
        actual=body_frame._read_dat(folder/'body.dat');return dict(execution='completed',runtime_s=time.monotonic()-started,address_space_limit_bytes=bound,**actual)
    except subprocess.TimeoutExpired as e:
        (folder/'stdout.log').write_bytes(e.stdout or b'');(folder/'stderr.log').write_bytes(e.stderr or b'');return dict(execution='interrupted',reason='bounded native timeout',runtime_s=time.monotonic()-started)
    except (OSError,subprocess.SubprocessError) as e:
        (folder/'launch-error.log').write_text(str(e));return dict(execution='tool_error',reason=str(e),runtime_s=time.monotonic()-started,address_space_limit_bytes=bound)
    except ValueError as e:return dict(execution='numerical_error',reason=str(e),runtime_s=time.monotonic()-started,address_space_limit_bytes=bound)


def evaluate(vehicle,parameters,output,*,root=ROOT,confirmation=False):
    p=_parameters(parameters)
    if vehicle['body_candidate_id']!=identity(vehicle['body_physical_definition']):raise ValueError('Mixed or mutated physical body identity')
    if vehicle.get('wheel_body',{}).get('parameters')!=p:raise ValueError('Body evaluation parameters differ from physical child')
    if _physical_body_parts(vehicle['geometry_parts'])!=vehicle['body_physical_definition']['geometry_parts']:raise ValueError('Actual car body stock differs from its declared body identity')
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh immutable candidate-body run directory required')
    output.mkdir(parents=True);variant=_analysis_variant(vehicle);(output/'candidate.json').write_bytes(encoded(vehicle));before=digest(__file__)
    modes=[('normal','accounted_cap_loaded_kg_per_car',.6,False,False,1.),('crowd','accounted_160_control_kg_per_car',.6,False,False,1.),('normal-fine','accounted_cap_loaded_kg_per_car',.3,False,False,1.)]
    if confirmation:modes += [('asymmetric-braking','accounted_cap_loaded_kg_per_car',.6,True,True,1.),('joint-sensitivity','accounted_cap_loaded_kg_per_car',.6,False,False,.1)]
    cases=[]
    for label,key,dx,asym,brake,jf in modes:
        mass=vehicle['mass'][key]-6730.;raw,mesh=body_solid_frame.deck(variant,mass,dx,asymmetric=asym,braking=brake,joint_factor=jf)
        if p['family']=='participating_sandwich':raw,extra=_sandwich(raw,variant,vehicle,dx);mesh.update(extra)
        case=dict(case=label,mesh=mesh,sprung_mass_kg=mass,**_native(raw,output/label))
        if case['execution']=='completed':
            residual=abs(case['support_reaction_z_N']+mesh['applied_vertical_force_N'])/abs(mesh['applied_vertical_force_N'])
            case.update(force_balance_relative_error=residual,numerical_validity='valid_equilibrium_only' if residual<1e-4 else 'invalid',engineering_screen=('unknown' if residual>=1e-4 else 'pass' if case['maximum_vertical_displacement_m']<=.0256 else 'fail'))
        cases.append(case)
    completed=[c for c in cases if c['execution']=='completed'];normal=next((c for c in completed if c['case']=='normal'),None);fine=next((c for c in completed if c['case']=='normal-fine'),None)
    refinement=abs(normal['maximum_vertical_displacement_m']-fine['maximum_vertical_displacement_m'])/fine['maximum_vertical_displacement_m'] if normal and fine else None
    missing=['Qualified laminate/core/bond constants and hot/wet properties','Joint slip, preload, bearing, fastener-hole and fatigue evidence','Stress, local/global buckling, crash and flexible modes','Bogie movement/worn-wheel/rail/cassette swept clearances','Complete installed stock, mass/CG/inertia and manufacturing qualification']
    if p['family']=='participating_sandwich':missing+=['Balanced-skin continuum is lower fidelity than ply-resolved laminate; ideal pad transfer and perfect internal bond are upper-bound hypotheses','Detailed floor/roof sandwich-to-frame load transfer remains unqualified; frame ribs/chords participate, their panel skins are not credited']
    balanced=len(completed)==len(cases) and all(c.get('force_balance_relative_error',1)<1e-4 for c in cases)
    mesh_confirmed=balanced and refinement is not None and refinement<.02
    state='fail' if any(c.get('engineering_screen')=='fail' for c in cases) else 'unknown'
    necessary='fail' if state=='fail' else 'pass' if mesh_confirmed and all(c.get('engineering_screen')=='pass' for c in cases) else 'unknown'
    result=dict(schema='osr-wheel-body-evaluation/1',candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],parameters=p,
        execution='completed' if len(completed)==len(cases) else 'completed_with_errors',numerical_validity='mesh_confirmed' if mesh_confirmed else 'invalid' if not balanced else 'unconfirmed',
        necessary_stiffness_screen=necessary,engineering_screen=state,evidence_maturity='analytical_constitutive_native_global_screen',
        states=dict(execution='completed' if len(completed)==len(cases) else 'completed_with_errors',numerical_validity='pass' if mesh_confirmed else 'invalid' if not balanced else 'unknown',engineering_screen=state,physical_acceptance='unknown'),
        metrics=dict(normal_deflection_m=normal['maximum_vertical_displacement_m'] if normal else None,normal_deflection_limit_m=.0256,refinement_fraction=refinement,
            accounted_tare_kg_per_car=vehicle['mass']['accounted_tare_kg_per_car'],stock_mass_delta_kg=vehicle['wheel_body']['stock_mass_delta_kg'],maximum_force_balance_residual=max((c.get('force_balance_relative_error',1) for c in cases),default=None)),
        cases=cases,native_jobs_used=len(cases),runtime_s=sum(c['runtime_s'] for c in cases),constitutive_hypotheses=CONSTITUTIVE,model_domain='Linear global continuum response; finite-deformation effects, local hole bearing, material strength and actual connector stiffness remain unevaluated',
        missing_gates=missing,raw_packages=[dict(path=str(output/c['case']),case=c['case']) for c in cases],source_sha256={**vehicle['source_sha256'],PRODUCER:before},**FLAGS)
    if before!=digest(__file__):raise ValueError('Body adapter source changed during native execution')
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result));manifest=dict(candidate_id=vehicle['candidate_id'],evaluation_id=result['evaluation_id'],source_sha256=result['source_sha256'],files_sha256={q.relative_to(output).as_posix():digest(q) for q in output.rglob('*') if q.is_file()},**FLAGS);manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return result


def patch_deck():
    """Uniaxial exact-field fixture for the synthetic balanced-skin continuum."""
    nodes={};lookup={};elements=[]
    def node(p):
        key=tuple(round(x,12) for x in p)
        if key not in lookup:lookup[key]=len(nodes)+1;nodes[lookup[key]]=list(p)
        return lookup[key]
    edges=((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7))
    for i in range(8):
        for j in range(2):
            a,b=i/8,(i+1)/8;c,d=j*.05,(j+1)*.05
            ps=[[a,0,c],[b,0,c],[b,.002,c],[a,.002,c],[a,0,d],[b,0,d],[b,.002,d],[a,.002,d]]
            ps += [[(ps[a][k]+ps[b][k])/2 for k in range(3)] for a,b in edges]
            elements.append([node(p) for p in ps])
    lines=['*HEADING','Synthetic balanced-skin exact uniaxial continuum fixture','*NODE']+[str(n)+','+','.join(map(str,p)) for n,p in nodes.items()]
    lines += ['*ELEMENT,TYPE=C3D20,ELSET=SKIN']
    for i,ids in enumerate(elements,1):lines += [str(i)+','+','.join(map(str,ids[:15]))+',',','.join(map(str,ids[15:]))]
    lines += ['*MATERIAL,NAME=SKIN','*ELASTIC,TYPE=ENGINEERING CONSTANTS',f'{SKIN_E},{SKIN_E},8e9,{SKIN_NU},.25,.25,4e9,3e9','3e9',
        '*ORIENTATION,NAME=SKIN_AXES','1.,0.,0.,0.,0.,1.','*SOLID SECTION,ELSET=SKIN,MATERIAL=SKIN,ORIENTATION=SKIN_AXES','*BOUNDARY']
    clamp=[n for n,p in nodes.items() if p[0]==0];tip=[n for n,p in nodes.items() if p[0]==1]
    lines += [f'{n},1,1' for n in clamp]
    anchor=lookup[(0.,0.,0.)];other=lookup[(0.,0.,.1)];lines += [f'{anchor},2,3',f'{other},2,2']
    for name,ids in [('TIP',tip),('BEARERS',clamp)]:
        lines += ['*NSET,NSET='+name]+[','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]
    lines += ['*STEP','*STATIC','*DLOAD']
    # Face4 is the x-positive surface for this explicitly listed brick ordering.
    lines += [f'{i},P4,-5000000.' for i in (15,16)]
    lines += ['*NODE PRINT,NSET=TIP','U','*NODE PRINT,NSET=BEARERS','RF','*END STEP','']
    return '\n'.join(lines),dict(force_N=1000.,length_m=1.,area_m2=.1*.002,E_Pa=SKIN_E,expected_extension_m=1000./(SKIN_E*.1*.002),elements=len(elements))


def run_patch_fixture(output):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh patch-fixture directory required')
    output.mkdir(parents=True);raw,definition=patch_deck();(output/'definition.json').write_bytes(encoded(dict(**definition,source_sha256=digest(__file__))))
    r=_native(raw,output/'native',60)
    if r['execution']=='completed':
        error=abs(r['maximum_longitudinal_displacement_m']-definition['expected_extension_m'])/definition['expected_extension_m'];force=abs(r['support_reaction_x_N']+1000.)/1000.
        r.update(relative_extension_error=error,force_balance_relative_error=force,numerical_screen='pass' if error<.01 and force<1e-5 else 'fail')
    result=dict(schema='osr-wheel-body-material-patch/1',definition=definition,native=r,native_jobs_used=1,
        scope='Exact uniaxial homogeneous balanced-skin continuum field only; no certified laminate/core/joints or whole-body qualification',source_sha256=digest(__file__),**FLAGS)
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result));return result
