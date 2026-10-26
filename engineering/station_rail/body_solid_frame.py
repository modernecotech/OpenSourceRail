"""Explicit C3D20R tube walls with translation-only rigid section-port equations.

Avoids unsupported static B32R rotational equations in CalculiX. Actual wall
volume is meshed. Rigid contact/load/support sections and connected ports are a joint upper
bound; all panel stiffness remains excluded. This is a numerical experiment.
"""
from pathlib import Path
import json,subprocess,os
from . import ROOT,FLAGS,body_frame
from .common import encoded,identity,digest,source_map
PRODUCER='engineering/station_rail/body_solid_frame.py'


def deck(variant,mass,dx=.6,asymmetric=False,braking=False,joint_factor=1.,mesh_override=None,clamped=False,nodal_loads=None):
    base=mesh_override if mesh_override is not None else body_frame._mesh(variant,dx);members=variant['members'];nodes=dict(base['nodes']);n=max(nodes)
    rotations={i:n+i for i in base['nodes']};nodes.update({rotations[i]:list(p) for i,p in base['nodes'].items()});n=max(nodes)
    lookup={};sections={};solids=[];volume=0.
    def node(member,p):
        nonlocal n
        key=(member,*[round(x,11) for x in p])
        if key not in lookup:n+=1;lookup[key]=n;nodes[n]=list(p)
        return lookup[key]
    edges=((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7))
    for element in base['elements']:
        i=element['member'];m=members[i];axis=m['axis'];u=(axis+1)%3;w=(axis+2)%3
        dim=m['section']['dimensions'];width,height=dim[:2]
        if m['section']['kind']=='BOX':
            up,wp,um,wm=dim[2:];us=[-width/2,-width/2+um,width/2-up,width/2];ws=[-height/2,-height/2+wm,height/2-wp,height/2]
        else:us=[-width/2,width/2];ws=[-height/2,height/2]
        c0,c1=[base['nodes'][k] for k in (element['nodes'][0],element['nodes'][2])];s0,s1=c0[axis],c1[axis]
        for ui in range(len(us)-1):
            for wi in range(len(ws)-1):
                if len(us)==4 and ui==1 and wi==1:continue
                a,b=us[ui:ui+2];c,d=ws[wi:wi+2]
                local=[(s0,a,c),(s1,a,c),(s1,b,c),(s0,b,c),(s0,a,d),(s1,a,d),(s1,b,d),(s0,b,d)]
                xyz=[]
                for s,t,v in local:
                    p=list(c0);p[axis]=s;p[u]+=t;p[w]+=v;xyz.append(p)
                xyz += [[(xyz[a][j]+xyz[b][j])/2 for j in range(3)] for a,b in edges]
                ids=[node(i,p) for p in xyz];solids.append((i,ids));volume+=(s1-s0)*(b-a)*(d-c)
        for centreid in element['nodes']:
            centre=base['nodes'][centreid];sections[i,round(centre[axis],11)]=centreid
    equations=[]
    port_refs=set(base['supports']) | {n for eq in base['equations'] for n,d,c in eq} | {n for x,ids in base['floor'] for n in ids}
    if nodal_loads is not None:port_refs.update(n for n,d,value in nodal_loads)
    for (i,*_),nid in lookup.items():
        m=members[i];p=nodes[nid];centreid=sections[i,round(p[m['axis']],11)]
        if centreid not in port_refs:continue
        centre=base['nodes'][centreid];r=[p[j]-centre[j] for j in range(3)];rot=rotations[centreid]
        cross={0:[(2,-r[2]),(3,r[1])],1:[(3,-r[0]),(1,r[2])],2:[(1,-r[1]),(2,r[0])]}
        for j in range(3):equations.append([(nid,j+1,1.),(centreid,j+1,-1.)]+[(rot,k,c) for k,c in cross[j] if abs(c)>1e-12])
    for eq in base['equations']:equations.append([(rotations[k] if d>3 else k,d-3 if d>3 else d,c) for k,d,c in eq])
    lines=['*HEADING','Actual stock C3D20R tube-wall frame, translation-only section equations','*NODE']
    lines += [str(k)+','+','.join(f'{v:.12g}' for v in p) for k,p in sorted(nodes.items())]
    grouped={}
    for eid,(i,ids) in enumerate(solids,1):grouped.setdefault(i,[]).append((eid,ids))
    for i,es in grouped.items():
        lines += [f'*ELEMENT,TYPE=C3D20R,ELSET=M{i}']
        for eid,ids in es:lines += [str(eid)+','+','.join(map(str,ids[:15]))+',',','.join(map(str,ids[15:]))]
    for name,factor in [('AL',1.),('JOINT',joint_factor)]:lines += [f'*MATERIAL,NAME={name}','*ELASTIC',f'{69e9*factor},.33']
    for i in grouped:lines += [f'*SOLID SECTION,ELSET=M{i},MATERIAL='+('JOINT' if members[i]['effective_joint'] else 'AL')]
    for eq in equations:lines += ['*EQUATION',str(len(eq)),','.join(f'{k},{d},{c:.12g}' for k,d,c in eq)]
    lines += ['*BOUNDARY']
    if clamped:
        for i in base['supports']:lines += [f'{i},1,3',f'{rotations[i]},1,3']
    else:
        lines += [f'{i},3,3' for i in base['supports']];support=sorted(base['supports'],key=lambda i:nodes[i][0]);lines += [f'{support[0]},1,2',f'{support[-1]},2,2']
    lines += ['*NSET,NSET=FRAME']
    refs=sorted(set(lookup.values()) | port_refs);lines += [','.join(map(str,refs[i:i+16])) for i in range(0,len(refs),16)]
    lines += ['*NSET,NSET=BEARERS',','.join(map(str,base['supports'])),'*STEP','*STATIC','*CLOAD'];total=0.;long=0.
    for k,(x,ids) in enumerate(base['floor']):
        prev=-8.5 if k==0 else (base['floor'][k-1][0]+x)/2;nxt=8.5 if k==len(base['floor'])-1 else (base['floor'][k+1][0]+x)/2
        for nid,share in zip(ids,(.75,.25) if asymmetric else (.5,.5)):
            fz=-mass*body_frame.G*(nxt-prev)/17*share;total+=fz;lines.append(f'{nid},3,{fz:.12g}')
            if braking:fx=mass*.6*(nxt-prev)/17*share;long+=fx;lines.append(f'{nid},1,{fx:.12g}')
    if nodal_loads is not None:
        for nid,dof,value in nodal_loads:
            lines.append(f'{nid},{dof},{value}')
            if dof==3:total+=value
            if dof==1:long+=value
    lines += ['*NODE PRINT,NSET=FRAME','U','*NODE PRINT,NSET=BEARERS','RF','*END STEP','']
    expected=sum(m['mass_kg']/2710 for i,m in enumerate(members) if i in variant['supported_member_indices'])
    if abs(volume-expected)>1e-8:raise ValueError('Explicit tube-wall volume differs from stock')
    return '\n'.join(lines),dict(nodes=len(nodes),solid_elements=len(solids),meshed_volume_m3=volume,expected_stock_volume_m3=expected,
        applied_vertical_force_N=total,applied_longitudinal_force_N=long,rigid_section_ports=True,rigid_ports_only_at_contacts_supports_loads=True,rotational_equation_dofs_used=False,displacement_output_scope='All actual solid nodes and active translational port nodes; rotation-variable nodes excluded')


def sill_stock_options(vehicle):
    """Three counted geometric alternatives; no structural or clearance pass."""
    from .vehicle import tube
    old=[m for m in body_frame.members_from_stock(vehicle['geometry_parts']) if m['id'].startswith('wheel-underframe/sill/')]
    options=[]
    for height,wall in ((.65,.012),(.65,.016),(.60,.016)):
        stock=[]
        label=f'180x{round(height*1000)}x{round(wall*1000)}mm'
        for i,m in enumerate(old):
            top=max(p['at_m'][2]+p['size_m'][2] for p in m['stock']);width=.18
            tube(stock,f'wheel-underframe/sill/alternative-{label}/{i}',(m['start_m'][0],m['start_m'][1]-width/2,top-height),m['length_m'],width,height,wall)
        physical=dict(parent_candidate_id=vehicle['candidate_id'],replaced_part_ids=[p['id'] for m in old for p in m['stock']],new_stock=stock)
        options.append(dict(alternative_id=identity(physical),name=label,physical_definition=physical,
            counted_material_mass_delta_kg=sum(p['mass_kg'] for p in stock)-sum(m['mass_kg'] for m in old),
            minimum_nominal_sill_bottom_m=min(p['at_m'][2] for p in stock),
            new_section_properties=[{k:m[k] for k in ('id','area_m2','I_about_local_1_m4','I_about_local_2_m4','mass_kg')} for m in body_frame.members_from_stock(stock)],
            execution='definition-only',structural_screen='unknown',clearance_screen='unknown',
            scope='Deep sills preserve width/top and require new bogie wear, suspension, wheel, rail and swept-envelope verification; no default adoption',**FLAGS))
    return options

def run_benchmark(output):
    from .vehicle import tube
    output=Path(output);output.mkdir();cases=[];L=10.;force=1000.;E=69e9
    expected=force*L**3/(3*E*(.18*.35**3-(.18-.016)*(.35-.016)**3)/12)
    stock=[];tube(stock,'wheel-underframe/sill/fixture',(0,-.09,-.175),L,.18,.35,.008)
    member=body_frame.members_from_stock(stock)[0];variant=dict(members=[member],supported_member_indices=[0])
    for count in (10,20):
        ns={i+1:[L*i/(2*count),0.,0.] for i in range(2*count+1)}
        base=dict(nodes=ns,elements=[dict(member=0,nodes=[2*i+1,2*i+2,2*i+3]) for i in range(count)],equations=[],supports=[1],floor=[])
        raw,mesh=deck(variant,0.,mesh_override=base,clamped=True,nodal_loads=[(2*count+1,3,-force)])
        folder=output/str(count);folder.mkdir();(folder/'frame.inp').write_text(raw)
        proc=subprocess.run(['/usr/bin/ccx','frame'],cwd=folder,capture_output=True,text=True,timeout=180,env={**os.environ,'OMP_NUM_THREADS':'1'})
        (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
        if proc.returncode or not (folder/'frame.dat').is_file():raise ValueError('Explicit-solid cantilever tool error')
        r=body_frame._read_dat(folder/'frame.dat');res=abs(r['support_reaction_z_N']-force)/force
        cases.append(dict(elements_axial=count,native_deflection_m=r['maximum_vertical_displacement_m'],Euler_m=expected,
            relative_error=(r['maximum_vertical_displacement_m']-expected)/expected,equilibrium_relative_error=res,mesh=mesh))
    return dict(cases=cases,numerical_screen='pass' if abs(cases[-1]['relative_error'])<.03 and all(c['equilibrium_relative_error']<1e-4 for c in cases) else 'fail',
        scope='Independent slender hollow-box cantilever with explicit-solid translation-only section interface')

def run(output,vehicle,root=ROOT):
    output=Path(output)
    if output.exists():raise ValueError('Fresh solid-frame directory required')
    output.mkdir(parents=True);definition=body_frame.build(vehicle,root);sources={**definition['source_sha256'],PRODUCER:digest(__file__)}
    (output/'definition.json').write_bytes(encoded(definition));cases=[];benchmark=run_benchmark(output/'independent-cantilever')
    for variant in definition['variants']:
        modes=[('normal-coarse','normal',.6,False,False,1.),('normal-fine','normal',.3,False,False,1.)]
        if variant['name']=='counted-post-base-connections':modes += [('empty','empty',.6,False,False,1.),('crowd','crowd',.6,False,False,1.),('asymmetric-braking','normal',.6,True,True,1.),('joint-compliance-surrogate','normal',.6,False,False,.1)]
        for label,load,dx,asym,brake,jf in modes:
            mass=vehicle['mass'][dict(normal='accounted_cap_loaded_kg_per_car',empty='accounted_tare_kg_per_car',crowd='accounted_160_control_kg_per_car')[load]]+variant['added_mass_kg']-6730.
            folder=output/(variant['name']+'-'+label);folder.mkdir();raw,mesh=deck(variant,mass,dx,asym,brake,jf);(folder/'frame.inp').write_text(raw)
            proc=subprocess.run(['/usr/bin/ccx','frame'],cwd=folder,capture_output=True,text=True,timeout=180,env={**os.environ,'OMP_NUM_THREADS':'1'})
            (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
            case=dict(variant=variant['name'],alternative_id=variant['alternative_id'],case=label,mesh=mesh,execution='tool-error',returncode=proc.returncode)
            if not proc.returncode and (folder/'frame.dat').is_file():
                try:
                    r=body_frame._read_dat(folder/'frame.dat');residual=abs(r['support_reaction_z_N']+mesh['applied_vertical_force_N'])/abs(mesh['applied_vertical_force_N'])
                    case.update(execution='completed',**r,vertical_force_balance_relative_error=residual,
                        necessary_deflection_screen='pass' if r['maximum_vertical_displacement_m']<=.0256 else 'fail',numerical_validity='equilibrium-pass' if residual<1e-4 else 'equilibrium-fail')
                except ValueError as error:case.update(execution='numerical-error',reason=str(error))
            cases.append(case)
    refinement=[]
    for v in definition['variants']:
        cs=[c for c in cases if c['variant']==v['name'] and c['case'] in ('normal-coarse','normal-fine') and c['execution']=='completed']
        if len(cs)==2:
            change=abs(cs[0]['maximum_vertical_displacement_m']-cs[1]['maximum_vertical_displacement_m'])/cs[1]['maximum_vertical_displacement_m'];refinement.append(dict(variant=v['name'],relative_deflection_change=change,numerical_screen='pass' if change<.02 and all(c['numerical_validity']=='equilibrium-pass' for c in cs) else 'fail'))
    if sources!={**body_frame.build(vehicle,root)['source_sha256'],PRODUCER:digest(__file__)}:raise ValueError('Solid frame source changed')
    result=dict(schema='osr-v06-native-solid-frame/1',parent_candidate_id=vehicle['candidate_id'],execution='completed' if all(c['execution']=='completed' for c in cases) else 'completed-with-errors',
        source_sha256=sources,cases=cases,refinement=refinement,independent_benchmark=benchmark,next_experiment_stock_options=sill_stock_options(vehicle),scope='Explicit hollow stock C3D20R, rigid contact/load/support-section and finite-contact port upper bound. No joints, stresses/buckling/fatigue or whole equipped-body qualification.',**FLAGS)
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result));m=dict(source_sha256=sources,files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS);m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return result


def verify(output,vehicle,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Solid-frame manifest differs')
    if m['source_sha256']!={**body_frame.build(vehicle,root)['source_sha256'],PRODUCER:digest(__file__)}:raise ValueError('Solid-frame source differs')
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Solid-frame identity differs')
    for name,h in m['files_sha256'].items():
        if digest(output/name)!=h:raise ValueError('Solid-frame payload differs')
    if any(r.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Solid frame cannot grant qualification')
    return dict(verified=True,evaluation_id=r['evaluation_id'],cases=len(r['cases']),**FLAGS)
