"""Same-candidate clevis-ear bearing-load FEM; no complete-launcher approval.

Input geometry is read-only. A quadratic O-grid follows the actual rectangular
plate and circular bore. The pin is replaced by distributed radial traction on
the forward half-bore; the attachment root is rigid. Neither is a contact/weld
qualification. FieldCraft and CalculiX solve the same declared linear model.
"""
from copy import deepcopy
from math import atan2,cos,sin,pi,sqrt,fsum,isfinite
from pathlib import Path
import json,os,re,resource,shutil,signal,subprocess,time
import platform
from . import native,identity
from .fieldcraft import batch_results

FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False,movement_authority=False)
SOURCE='engineering/design_search/craft_backends/launch_component_fem.py'
SCREENS=dict(force_relative=1e-6,displacement_refinement_relative=.02,
             sampled_bore_stress_refinement_relative=.05,cross_solver_displacement_relative=.01)
CORNERS=((0,0,0),(2,0,0),(2,2,0),(0,2,0),(0,0,2),(2,0,2),(2,2,2),(0,2,2))
EDGES=((1,0,0),(2,1,0),(1,2,0),(0,1,0),(1,0,2),(2,1,2),(1,2,2),(0,1,2),
       (0,0,1),(2,0,1),(2,2,1),(0,2,1))


def sources():
    folder=Path(__file__).parent;root=folder.parents[2]
    return {p.relative_to(root).as_posix():native.digest(p) for p in
        (Path(__file__),folder/'native.py',folder/'fieldcraft.py',folder/'__init__.py',folder/'cases.py',folder/'tools.json')}


def from_assembly(assembly):
    """Authenticate the read-only CAD contract; derive no new physical parts."""
    a=assembly
    if a.get('assembly_definition_id')!=identity({k:v for k,v in a.items() if k!='assembly_definition_id'}):raise ValueError('Assembly definition seal differs')
    if a.get('candidate_id')!=identity(a['physical_definition']):raise ValueError('Physical assembly identity differs')
    g=a['component_geometry'];f=a['fem_interface'];d=f['dimensions'];m=f['material_hypothesis']
    if f.get('units')!=dict(force='N',length='m',stress='Pa'):raise ValueError('CAD/FEM interface units must be explicit SI')
    if a['component_geometry_id']!=identity(g) or f['component_geometry_id']!=a['component_geometry_id'] or f['candidate_id']!=a['candidate_id']:
        raise ValueError('Mixed CAD/FEM component identity')
    if any(a.get(k,False) is not False or f.get(k,False) is not False for k in FLAGS):raise ValueError('Assembly cannot grant release')
    if len(g['parts'])!=2 or f['force_direction']!=[1,0,0]:raise ValueError('Two-ear +x load contract required')
    physical_parts={p['id']:p for p in a['physical_definition']['parts']}
    if any(physical_parts.get(p['id'])!=p for p in g['parts']):raise ValueError('Component is not the same physical assembly subset')
    transform=g.get('analysis_frame_to_station',g.get('component_frame'))
    if 'parts_coordinate_frame' in g and g['parts_coordinate_frame']!='station':raise ValueError('Explicit station-frame CAD parts required')
    if transform['rotation_matrix']!=[[1,0,0],[0,1,0],[0,0,1]] or transform['translation_to_station_m']!=d['ear_parent_translation_m']:
        raise ValueError('Explicit unrotated component transform required')
    for part,y in zip(g['parts'],d['ear_local_y_m']):
        if (part['shape']!='box' or part['size_m']!=[d['ear_length_m'],d['ear_thickness_m'],d['ear_height_m']]
            or part['at_m']!=[transform['translation_to_station_m'][0],y,transform['translation_to_station_m'][2]]
            or part['holes']!=[dict(axis='y',diameter_m=d['bore_diameter_m'],x_m=d['bore_center_local_xz_m'][0],z_m=d['bore_center_local_xz_m'][1])]):
            raise ValueError('FEM dimensions do not match the CAD plates and bores')
    pin=physical_parts.get('clevis/pin')
    if pin is not None and (pin.get('shape')!='cylinder' or 2*pin['radius_m']!=d['pin_diameter_m']):
        raise ValueError('Analytical pin diameter differs from the CAD pin')
    result=dict(candidate_id=a['candidate_id'],component_geometry_id=a['component_geometry_id'],units='m-kg-s-N-Pa',
        length_m=d['ear_length_m'],height_m=d['ear_height_m'],thickness_m=d['ear_thickness_m'],
        bore_diameter_m=d['bore_diameter_m'],bore_x_m=d['bore_center_local_xz_m'][0],bore_z_m=d['bore_center_local_xz_m'][1],
        y_base_m=d['ear_local_y_m'][0],force_per_ear_N=f['force_per_ear_N'],pin_force_N=f['total_force_N'],
        pin_diameter_m=d['pin_diameter_m'],ear_center_span_m=abs(d['ear_local_y_m'][1]-d['ear_local_y_m'][0]),
        central_eye_contact_width_bound_m=[0.,d['clear_gap_m']],
        young_Pa=m['young_Pa'],poisson=m['poisson'],density_kg_m3=m['density_kg_m3'],
        installed_translation_m=d['ear_parent_translation_m'],component_geometry=deepcopy(g),
        source_assembly_definition_id=a['assembly_definition_id'],source_interface_sha256=identity(f),
        material_hypothesis=deepcopy(m),**FLAGS)
    return validate(result)


def validate(spec):
    """Explicit physical IDs and SI data; no material/force defaults."""
    if spec.get('units')!='m-kg-s-N-Pa':raise ValueError('Explicit SI component contract required')
    for k in ('candidate_id','component_geometry_id'):
        if not re.fullmatch('[a-f0-9]{64}',str(spec.get(k,''))):raise ValueError('Explicit physical candidate/component identity required')
    for k in ('length_m','height_m','thickness_m','bore_diameter_m','force_per_ear_N','pin_force_N','young_Pa','density_kg_m3'):
        if type(spec.get(k)) not in (int,float) or not isfinite(spec[k]) or spec[k]<=0:raise ValueError('Positive finite SI '+k+' required')
    for k in ('y_base_m','bore_x_m','bore_z_m','poisson'):
        if type(spec.get(k)) not in (int,float) or not isfinite(spec[k]):raise ValueError('Finite SI '+k+' required')
    r=spec['bore_diameter_m']/2
    if not r<spec['bore_x_m']<spec['length_m']-r or not r<spec['bore_z_m']<spec['height_m']-r:
        raise ValueError('Bore must be wholly within the plate')
    if not 0<=spec['poisson']<.5 or abs(2*spec['force_per_ear_N']-spec['pin_force_N'])>1e-8:
        raise ValueError('Two equal ear load paths and valid elastic material required')
    pin=spec.get('pin_diameter_m',spec['bore_diameter_m'])
    if type(pin) not in (int,float) or not isfinite(pin) or not 0<pin<=spec['bore_diameter_m']:raise ValueError('Pin must fit the declared bore')
    if any(spec.get(k,False) is not False for k in FLAGS):raise ValueError('Research cannot confer acceptance')
    return spec


def analytical(spec):
    validate(spec);s=spec;F=s['force_per_ear_N'];t=s['thickness_m'];d=s['bore_diameter_m']
    clear=s['length_m']-s['bore_x_m']-d/2
    volume=s['length_m']*s['height_m']*t-pi*(d/2)**2*t
    pin=s.get('pin_diameter_m',d);span=s.get('ear_center_span_m');width=s.get('central_eye_contact_width_bound_m')
    bending=None
    if span is not None:
        if not isinstance(width,list) or len(width)!=2 or not 0<=width[0]<=width[1]<=span:raise ValueError('Bounded central-eye contact width required')
        moments=[s['pin_force_N']*(2*span-b)/8 for b in reversed(width)]
        stresses=[32*M/(pi*pin**3) for M in moments]
        shear=s['pin_force_N']/(2*pi*pin*pin/4)
        bending=dict(ear_support_centre_span_m=span,central_eye_uniform_contact_width_bound_m=width,
            maximum_moment_bound_Nm=moments,outer_fibre_bending_nominal_bound_Pa=stresses,
            conservative_noncoincident_vm_bound_Pa=[sqrt(x*x+3*(4*shear/3)**2) for x in stresses],
            assumptions='Simply supported pin at ear centres; symmetric uniform central-eye patch to point-load limit; ignores support compliance/contact indentation, fillets, retention, impact and fatigue',
            combination_scope='Conservative envelope combining separate bending and transverse-shear maxima; not a co-located 3D stress solution',
            strength_qualification=False)
    return dict(net_section_nominal_Pa=F/(t*(s['height_m']-d)),bearing_nominal_Pa=F/(t*d),
        forward_edge_shear_nominal_Pa=F/(2*t*clear),pin_double_shear_nominal_Pa=s['pin_force_N']/(2*pi*pin*pin/4),pin_bending=bending,
        single_ear_material_volume_m3=volume,single_ear_material_mass_kg=volume*s['density_kg_m3'],
        material_strength_qualified=False,scope='Nominal section/bearing/shear and bounded pin-beam stresses; local concentrations, weld/contact and fatigue qualification excluded',**FLAGS)


def _angles(s,n):
    if n not in (32,64):raise ValueError('Only predeclared 32/64-sector meshes admitted')
    cx,cz=s['bore_x_m'],s['bore_z_m']
    breaks=sorted(set([0.,pi/2,pi,3*pi/2,2*pi]+[atan2(z-cz,x-cx)%(2*pi)
        for x,z in ((0,0),(s['length_m'],0),(s['length_m'],s['height_m']),(0,s['height_m']))]))
    if len(breaks)!=9:raise ValueError('Pilot requires an off-centre bore with eight distinct angular sectors')
    per=n//8
    values=[a+(b-a)*i/(2*per) for a,b in zip(breaks,breaks[1:]) for i in range(2*per)]
    probes=sorted([*breaks[:-1],*[(a+b)/2 for a,b in zip(breaks,breaks[1:])]])
    return values,probes


def mesh(spec,level='coarse'):
    validate(spec);s=spec
    if level not in ('coarse','fine'):raise ValueError('Declared coarse/fine level required')
    nt,nr,ny=(32,4,2) if level=='coarse' else (64,8,2)
    angles,probes=_angles(s,nt);cx,cz=s['bore_x_m'],s['bore_z_m'];r=s['bore_diameter_m']/2
    nodes={};index={}
    def position(i,j,k):
        a=angles[i%(2*nt)];c,q=cos(a),sin(a);limits=[]
        if abs(c)>1e-14:limits.append(((s['length_m']-cx) if c>0 else -cx)/c)
        if abs(q)>1e-14:limits.append(((s['height_m']-cz) if q>0 else -cz)/q)
        outside=min(v for v in limits if v>0)
        radial=r+(outside-r)*(j/(2*nr))**1.35
        return [cx+radial*c,s['y_base_m']+s['thickness_m']*k/(2*ny),cz+radial*q]
    for i in range(2*nt):
        for j in range(2*nr+1):
            for k in range(2*ny+1):
                if (i%2)+(j%2)+(k%2)>1:continue
                number=len(nodes)+1;index[i,j,k]=number;nodes[number]=position(i,j,k)
    elements={}
    for i in range(nt):
        for j in range(nr):
            for k in range(ny):
                elements[len(elements)+1]=[index[(2*i+a)%(2*nt),2*j+b,2*k+c] for a,b,c in CORNERS+EDGES]
    root=[n for n,p in nodes.items() if abs(p[0])<1e-10]
    bore=[n for (i,j,k),n in index.items() if j==0]
    # Consistent Q8 face integration. Constant radial pressure on the forward
    # semicylinder has p=F/(t*d), not a point force and not tensile back-bore load.
    qpoints=[(-sqrt(3/5),5/9),(0.,8/9),(sqrt(3/5),5/9)]
    pressure=s['force_per_ear_N']/(s['thickness_m']*2*r);loads={}
    def shape(u,v):return [-(1-u)*(1-v)*(1+u+v)/4,-(1+u)*(1-v)*(1-u+v)/4,
        -(1+u)*(1+v)*(1-u-v)/4,-(1-u)*(1+v)*(1+u-v)/4,
        (1-u*u)*(1-v)/2,(1+u)*(1-v*v)/2,(1-u*u)*(1+v)/2,(1-u)*(1-v*v)/2]
    for i in range(nt):
        a=angles[2*i];b=angles[(2*i+2)%(2*nt)] if i<nt-1 else 2*pi
        if cos((a+b)/2)<=0:continue
        for k in range(ny):
            face=[index[(2*i+da)%(2*nt),0,2*k+dk] for da,dk in ((0,0),(2,0),(2,2),(0,2),(1,0),(2,1),(1,2),(0,1))]
            for u,wu in qpoints:
                theta=(a+b)/2+u*(b-a)/2
                for v,wv in qpoints:
                    area=r*(b-a)/2*s['thickness_m']/ny/2*wu*wv
                    force=[pressure*cos(theta)*area,0.,pressure*sin(theta)*area]
                    for number,N in zip(face,shape(u,v)):
                        loads.setdefault(number,[[],[],[]])
                        for d in range(3):loads[number][d].append(N*force[d])
    loads={n:[fsum(v) for v in parts] for n,parts in loads.items()}
    total=fsum(v[0] for v in loads.values());scale=s['force_per_ear_N']/total
    loads={n:[x*scale for x in v] for n,v in loads.items()}
    targets=[[cx+r*cos(a),s['y_base_m']+s['thickness_m']/2,cz+r*sin(a)] for a in probes]
    probe_nodes=[]
    for p in targets:
        n=min(bore,key=lambda n:sum((a-b)**2 for a,b in zip(nodes[n],p)))
        if max(abs(a-b) for a,b in zip(nodes[n],p))>1e-10:raise ValueError('Probe is not an exact shared mesh point')
        probe_nodes.append(n)
    value=dict(level=level,nodes={str(n):p for n,p in nodes.items()},elements={str(n):p for n,p in elements.items()},
        root_nodes=root,bore_nodes=bore,probe_nodes=probe_nodes,probe_xyz_m=targets,
        nodal_load_N={str(n):v for n,v in loads.items()},applied_N=[fsum(v[d] for v in loads.values()) for d in range(3)],
        element_type='hex20',angular_elements=nt,radial_elements=nr,through_thickness_elements=ny,
        geometry='Quadratic O-grid; curved bore midside nodes on CAD circle; outer boundary on exact rectangle',
        load='Constant radial compressive traction on +x half-bore, Q8 consistent integration, exact resultant normalization',
        support='All translations fixed on x=0 attachment edge; weld/base flexibility absent',
        input_sha256=identity(spec),candidate_id=s['candidate_id'],component_geometry_id=s['component_geometry_id'])
    value['mesh_id']=identity(value)
    return value


def commands(spec,model):
    validate(spec)
    cmd=lambda c,**p:dict(command=c,params=p)
    out=[cmd('model.units',system='m-kg-s-N-Pa')]
    out += [cmd('mesh.node.add',label=int(n),xyz=p) for n,p in model['nodes'].items()]
    out += [cmd('mesh.element.add',label=int(n),kind='hex20',nodes=e) for n,e in model['elements'].items()]
    out += [cmd('model.set.create',name='Body',elements=list(map(int,model['elements']))),
        cmd('model.set.create',name='Root',nodes=model['root_nodes']),
        cmd('model.material.create',name='DeclaredSteel',elastic=dict(type='isotropic',young=spec['young_Pa'],poisson=spec['poisson'])),
        cmd('model.section.create',name='Ear',set='Body',material='DeclaredSteel',kind=dict(type='solid')),
        cmd('model.boundary_condition.create',name='RigidRoot',type='fixed',target=dict(set='Root'))]
    for n,force in model['nodal_load_N'].items():
        out.append(cmd('model.set.create',name='BearingNode-'+n,nodes=[int(n)]))
        out.append(cmd('model.load.create',name='Bearing-'+n,type='force',target=dict(set='BearingNode-'+n),vector=force,distribution='total'))
    out += [cmd('model.step.create',name='Bearing',procedure=dict(type='static'),boundary_conditions=['RigidRoot'],
        loads=['Bearing-'+n for n in model['nodal_load_N']]),cmd('model.check'),cmd('solve.static',step='Bearing'),
        cmd('solve.probe',step='Bearing',at=model['probe_xyz_m']),cmd('results.reactions',step='Bearing',sets=['Root']),cmd('model.info')]
    return out


def parse_field(value,model):
    rows=batch_results(value);check,solve,probe,reaction,info=rows[-5:]
    if check.get('errors')!=0 or not check.get('ready') or info.get('display_units')!='m-kg-s-N-Pa':raise ValueError('Native model/units check failed')
    if probe.get('units',{}).get('stress')!='Pa' or probe.get('units',{}).get('xyz')!='m':raise ValueError('SI readbacks required')
    if info.get('nodes')!=len(model['nodes']) or info.get('elements')!={'hex20':len(model['elements'])}:raise ValueError('Native mesh counts differ')
    if reaction.get('stale') is not False or reaction.get('units',{}).get('force')!='N':raise ValueError('Current SI support reactions required')
    nodes=probe['nodes']
    if len(nodes)!=len(model['probe_xyz_m']):raise ValueError('Exact sampled bore coverage required')
    for row,p in zip(nodes,model['probe_xyz_m']):
        if max(abs(a-b) for a,b in zip(row['xyz'],p))>1e-9:raise ValueError('Probe location differs')
        if any(not isfinite(x) for x in [*row['displacement'],row['von_mises']]):raise ValueError('Nonfinite component readback')
    force=reaction['total']['force'];res=max(abs(a+b) for a,b in zip(force,model['applied_N']))/abs(model['applied_N'][0])
    return dict(displacement_at_forward_bore_m=nodes[0]['displacement'],sampled_bore_peak_von_mises_Pa=max(n['von_mises'] for n in nodes),
        sampled_bore_points=nodes,reaction_N=force,reaction_moment_Nm=reaction['total']['moment'],
        applied_N=model['applied_N'],force_equilibrium_relative_residual=res,force_equilibrium_passed=res<=SCREENS['force_relative'],
        node_count=info['nodes'],elements=info['elements'],stress_scope='Maximum of16 common mid-thickness bore points, not global stress or a certified failure criterion',**FLAGS)


def deck(spec,model):
    lines=['*HEADING','OSR actual research clevis ear; SI; radial half-bore load; rigid root','*NODE']
    # CalculiX's numeric card fields reject very long Python float spellings,
    # notably tiny negative roundoff at x=0. Twelve significant digits bound
    # coordinate serialization error far below this component's mesh tolerance.
    lines += [n+','+','.join(f'{v:.12g}' for v in p) for n,p in model['nodes'].items()]
    lines += ['*ELEMENT,TYPE=C3D20,ELSET=BODY']
    for n,e in model['elements'].items():lines += [','.join(map(str,[n,*e[:15]]))+',',','.join(map(str,e[15:]))]
    for name,numbers in [('ROOT',model['root_nodes']),('TIP',model['probe_nodes'])]:
        lines.append('*NSET,NSET='+name)
        lines += [','.join(map(str,numbers[i:i+15])) for i in range(0,len(numbers),15)]
    lines += ['*MATERIAL,NAME=STEEL','*ELASTIC',f"{spec['young_Pa']},{spec['poisson']}",
        '*SOLID SECTION,ELSET=BODY,MATERIAL=STEEL','*BOUNDARY','ROOT,1,3','*STEP','*STATIC','*CLOAD']
    for n,v in model['nodal_load_N'].items():
        lines += [f'{n},{d+1},{f:.12g}' for d,f in enumerate(v) if abs(f)>1e-12]
    return '\n'.join(lines+['*NODE PRINT,NSET=TIP','U','*NODE PRINT,NSET=ROOT','RF','*EL PRINT,ELSET=BODY','S','*END STEP',''])


def parse_ccx(text,model):
    values={'u':{},'rf':{}};mode=None;stresses=[]
    for line in text.splitlines():
        low=line.lower()
        if 'displacements' in low:mode='u' if 'set tip' in low else None
        elif 'forces' in low:mode='rf' if 'set root' in low else None
        elif 'stresses' in low:mode='s'
        else:
            f=line.split()
            if mode in ('u','rf') and len(f)==4 and f[0].isdigit():values[mode][int(f[0])]=[float(x.replace('D','E')) for x in f[1:]]
            elif mode=='s' and len(f)==8 and f[0].isdigit():
                xx,yy,zz,xy,xz,yz=map(float,f[2:]);stresses.append(sqrt(((xx-yy)**2+(yy-zz)**2+(zz-xx)**2)/2+3*(xy*xy+xz*xz+yz*yz)))
    if set(values['u'])!=set(model['probe_nodes']) or set(values['rf'])!=set(model['root_nodes']):raise ValueError('Independent solver coverage differs')
    reaction=[fsum(v[d] for v in values['rf'].values()) for d in range(3)]
    residual=max(abs(a+b) for a,b in zip(reaction,model['applied_N']))/abs(model['applied_N'][0])
    return dict(displacement_at_forward_bore_m=values['u'][model['probe_nodes'][0]],reaction_N=reaction,
        force_equilibrium_relative_residual=residual,force_equilibrium_passed=residual<=SCREENS['force_relative'],
        integration_point_peak_von_mises_Pa=max(stresses) if stresses else None,
        stress_scope='Global integration-point maximum includes rigid-root concentrations; not directly comparable to FieldCraft sampled nodal stress',**FLAGS)


def _ccx(spec,model,folder):
    folder.mkdir();native.write(folder/'mesh.json',model);(folder/'component.inp').write_text(deck(spec,model))
    tools={n:shutil.which(n) for n in ('ccx','bwrap','time')}
    if not all(tools.values()):raise ValueError('Bounded independent CalculiX tools unavailable')
    args=[tools['time'],'-f','{"peak_rss_kib":%M,"wall_s":%e}', '-o',str(folder/'usage.json'),tools['bwrap'],
        '--die-with-parent','--unshare-net','--ro-bind','/','/','--dev','/dev','--bind',str(folder),str(folder),'--chdir',str(folder),'--',tools['ccx'],'component']
    native.write(folder/'invocation.json',dict(argv=args,tool_sha256={n:native.digest(p) for n,p in tools.items()},timeout_s=120,memory_mb=2048))
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,)*2);resource.setrlimit(resource.RLIMIT_CPU,(120,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
    env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','CCX_NPROC_RESULTS':'1','CCX_NPROC_EQUATION_SOLVER':'1'}
    started=time.monotonic()
    with (folder/'stdout.log').open('wb') as out,(folder/'stderr.log').open('wb') as err:
        p=subprocess.Popen(args,cwd=folder,stdout=out,stderr=err,env=env,preexec_fn=limits,start_new_session=True)
        try:code=p.wait(timeout=120)
        except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();raise ValueError('Independent solve timed out; failed execution retained')
    if code:raise ValueError('Independent solve failed; inspect retained stdout/stderr')
    result=parse_ccx((folder/'component.dat').read_text(),model);result.update(elapsed_s=time.monotonic()-started)
    native.write(folder/'result.json',result);return result


def run(spec,output):
    """Four bounded native jobs; immutable input/logs, same physical identity."""
    validate(spec)
    if not spec.get('source_assembly_definition_id') or identity(spec.get('component_geometry'))!=spec['component_geometry_id']:
        raise ValueError('Native admission requires the authenticated CAD assembly contract')
    folder=Path(output).resolve();folder.mkdir(parents=True,exist_ok=False)
    native.write(folder/'input.json',spec);source=native.digest(__file__);context=sources();results={}
    (folder/'evaluator-source.py').write_bytes(Path(__file__).read_bytes())
    request=dict(candidate_id=spec['candidate_id'],component_geometry_id=spec['component_geometry_id'],input_sha256=identity(spec),
        source_sha256=context,tools={n:native.pin(n) for n in ('solidcraft','fieldcraft')},screens=SCREENS,
        runtime=dict(python=platform.python_version(),platform=platform.platform(),
                     ccx_sha256=native.digest(shutil.which('ccx')) if shutil.which('ccx') else None),
        solver_scope='Actual isolated clevis-ear solid, prescribed bearing traction and rigid-root hypothesis',**FLAGS)
    request['evaluation_id']=identity(request);native.write(folder/'request.json',request)
    for level in ('coarse','fine'):
        model=mesh(spec,level);native.write(folder/(level+'-mesh.json'),model)
        cmds=commands(spec,model);calls=[('batch',dict(commands=cmds[i:i+4000])) for i in range(0,len(cmds),4000)]
        try:
            execution,replies=native.mcp('fieldcraft',calls,folder/('fieldcraft-'+level),read_root=folder,timeout_s=120,memory_mb=2048)
            if execution['execution']!='executed':raise ValueError('FieldCraft process did not complete')
            all_rows=[]
            for i,(_,call) in enumerate(calls,2):
                raw=next(r for r in replies if r.get('id')==i)
                # Preserve the entire raw batch in stdout, but summarize its
                # actual failure rather than embedding thousands of prior rows.
                if raw.get('result',{}).get('isError'):
                    texts=[c['text'] for c in raw['result'].get('content',[]) if c.get('type')=='text']
                    try:failed=json.loads(texts[0]).get('failed')
                    except (IndexError,ValueError,AttributeError):failed=None
                    if failed:raise ValueError('FieldCraft command failed: '+str(failed))
                all_rows.extend(batch_results(native.payload(raw),len(call['commands'])))
            field=parse_field(dict(ok=True,failed=None,completed=len(all_rows),results=all_rows),model)
            ccx=_ccx(spec,model,folder/('calculix-'+level))
            difference=abs(field['displacement_at_forward_bore_m'][0]-ccx['displacement_at_forward_bore_m'][0])/abs(ccx['displacement_at_forward_bore_m'][0])
            results[level]=dict(state='completed',fieldcraft=field,calculix=ccx,
                cross_solver_displacement_relative_difference=difference,cross_solver_screen_passed=difference<=SCREENS['cross_solver_displacement_relative'])
        except (ValueError,OSError,KeyError,StopIteration) as exc:
            results[level]=dict(state='held',reason=str(exc))
            if level=='coarse':
                results['fine']=dict(state='deferred',reason='Resolve the coarse definition/execution before refinement')
                break
    refinement=compare_refinement(results)
    if sources()!=context:raise ValueError('Evaluator dependencies changed during execution; outputs retained without promotion')
    result=dict(schema='osr-launch-clevis-fem/1',evaluation_id=request['evaluation_id'],candidate_id=spec['candidate_id'],
        component_geometry_id=spec['component_geometry_id'],analytical=analytical(spec),levels=results,refinement=refinement,
        unresolved=['Actual pin contact, clearance, friction and retention','Root weld/base flexibility, residual stress and attachment reactions',
            'Load reversal, fatigue, material certificates and independently approved limits','Complete shuttle/frame/guideway and train compression dynamics',
            'Available launcher force, repeated duty, control protection and independent braking'],**FLAGS)
    result['artifact_sha256']={str(p.relative_to(folder)):native.digest(p) for p in folder.rglob('*') if p.is_file()}
    result['result_id']=identity(result);native.write(folder/'result.json',result);return result


def compare_refinement(results):
    if not all(r['state']=='completed' for r in results.values()):return None
    c,f=[results[n]['fieldcraft'] for n in ('coarse','fine')]
    u=abs(c['displacement_at_forward_bore_m'][0]-f['displacement_at_forward_bore_m'][0])/abs(f['displacement_at_forward_bore_m'][0])
    stress=abs(c['sampled_bore_peak_von_mises_Pa']-f['sampled_bore_peak_von_mises_Pa'])/f['sampled_bore_peak_von_mises_Pa']
    return dict(displacement_relative_change=u,sampled_bore_stress_relative_change=stress,
        displacement_screen_passed=u<=SCREENS['displacement_refinement_relative'],sampled_stress_screen_passed=stress<=SCREENS['sampled_bore_stress_refinement_relative'],mesh_independence_established=False)


def verify(output,assembly):
    """Read-only integrity/recomputation; no new native solve or qualification."""
    folder=Path(output).resolve();result=json.loads((folder/'result.json').read_bytes())
    if result['result_id']!=identity({k:v for k,v in result.items() if k!='result_id'}):raise ValueError('FEM result seal differs')
    request=json.loads((folder/'request.json').read_bytes());spec=from_assembly(assembly)
    if request['evaluation_id']!=identity({k:v for k,v in request.items() if k!='evaluation_id'}):raise ValueError('Evaluation request differs')
    if request['source_sha256']!=sources() or (folder/'evaluator-source.py').read_bytes()!=Path(__file__).read_bytes():raise ValueError('Evaluator source epoch differs')
    if json.loads((folder/'input.json').read_bytes())!=spec or request['input_sha256']!=identity(spec):raise ValueError('Mixed CAD/FEM inputs')
    for key in ('candidate_id','component_geometry_id','evaluation_id'):
        if result.get(key)!=request.get(key):raise ValueError('Mixed FEM result '+key)
    if set(result['levels'])!={'coarse','fine'}:raise ValueError('Declared mesh-level coverage differs')
    if any(result.get(k) is not False for k in FLAGS):raise ValueError('Component calculation cannot grant release')
    files={p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file() and p!=folder/'result.json'}
    if set(files)!=set(result['artifact_sha256']):raise ValueError('Native artifact coverage differs')
    for name,path in files.items():
        if path.is_symlink() or native.digest(path)!=result['artifact_sha256'][name]:raise ValueError('Native artifact changed: '+name)
    for level,row in result['levels'].items():
        if row['state']!='completed':continue
        model=mesh(spec,level)
        if model!=json.loads((folder/(level+'-mesh.json')).read_bytes()):raise ValueError('Same-candidate mesh differs')
        invocation=json.loads((folder/('fieldcraft-'+level)/'invocation.json').read_bytes())
        messages=[json.loads(line) for line in invocation['stdin'].splitlines()]
        submitted=[c for msg in messages if msg.get('method')=='tools/call' for c in msg['params']['arguments']['commands']]
        if submitted!=commands(spec,model):raise ValueError('Native source-bound command request differs')
        replies=[json.loads(line) for line in (folder/('fieldcraft-'+level)/'stdout.jsonl').read_text().splitlines()]
        rows=[]
        for reply in replies:
            if reply.get('id',0)>1:rows.extend(batch_results(native.payload(reply)))
        parsed=parse_field(dict(ok=True,failed=None,completed=len(rows),results=rows),model)
        if parsed!=row['fieldcraft']:raise ValueError('FieldCraft component readback differs')
        ccx=parse_ccx((folder/('calculix-'+level)/'component.dat').read_text(),model)
        if ccx!={k:v for k,v in row['calculix'].items() if k!='elapsed_s'}:raise ValueError('Independent solver readback differs')
        if (folder/('calculix-'+level)/'component.inp').read_text()!=deck(spec,model):raise ValueError('Independent geometry/load deck differs')
    if result['analytical']!=analytical(spec):raise ValueError('Analytical load-path bound differs')
    if result['refinement']!=compare_refinement(result['levels']):raise ValueError('Recomputed refinement differs')
    return dict(integrity_verified=True,fresh_native_solve=False,result_id=result['result_id'],candidate_id=spec['candidate_id'],
                component_geometry_id=spec['component_geometry_id'],scope='Stored component evidence only; not an OS-isolated or authenticated physical verifier',**FLAGS)
