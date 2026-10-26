"""Stock-derived 3D body-frame experiment, with counted post-base connections.

B32R members reduce the actual rectangular tube stock, with rigid section-offset
constraints ONLY at finite-area material contacts. Those fully rigid welds are
an upper-bound joint hypothesis. No GFRP panel shear or glass/door stiffness is
credited. A compliant-connection sensitivity never establishes a real joint law.
"""
from collections import defaultdict
from pathlib import Path
from math import ceil,sqrt,isfinite
import json,os,re,subprocess
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map
from .vehicle import box

PRODUCER='engineering/station_rail/body_frame.py'
G=9.80665
IDS=('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')
REFERENCE='https://www.dhondt.de/ccx_2.16.pdf'


def _contact(a,b,tol=1e-8):
    lo=[max(a['at_m'][i],b['at_m'][i]) for i in range(3)]
    hi=[min(a['at_m'][i]+a['size_m'][i],b['at_m'][i]+b['size_m'][i]) for i in range(3)]
    depth=[b-a for a,b in zip(lo,hi)]
    if min(depth)<-tol or sum(d>tol for d in depth)<2:return None
    return [(a+b)/2 for a,b in zip(lo,hi)]


def members_from_stock(parts):
    """Four disjoint tube walls -> exact areas/second moments; no allocation I."""
    groups=defaultdict(list)
    for p in parts:
        if p.get('kind')!='box':continue
        if p['id'].startswith('comfort-shell/replacement-frame/'):
            groups[p['id'].rsplit('/',2)[0]].append(p)
        elif p['id'].startswith(('wheel-underframe/sill/','wheel-underframe/bolster/','wheel-underframe/secondary-tie/')):
            groups[p['id'].rsplit('/',1)[0]].append(p)
        elif p['id'].startswith('body-post-connection/'):
            groups[p['id']].append(p)
    members=[]
    for name,stock in sorted(groups.items()):
        if len(stock) not in (1,4):raise ValueError('Complete rectangular stock section required: '+name)
        lo=[min(p['at_m'][i] for p in stock) for i in range(3)]
        hi=[max(p['at_m'][i]+p['size_m'][i] for p in stock) for i in range(3)]
        ext=[b-a for a,b in zip(lo,hi)];axis=max(range(3),key=lambda i:ext[i]);u=(axis+1)%3;w=(axis+2)%3
        length=ext[axis]
        if any(abs(p['size_m'][axis]-length)>1e-7 for p in stock):raise ValueError('Extrusion walls must share full length')
        area=sum(p['volume_m3']/length for p in stock)
        centre=[sum(p['volume_m3']*p['cg_m'][i] for p in stock)/sum(p['volume_m3'] for p in stock) for i in range(3)]
        Iu=sum((p['volume_m3']/length)*(p['size_m'][w]**2/12+(p['cg_m'][w]-centre[w])**2) for p in stock)
        Iw=sum((p['volume_m3']/length)*(p['size_m'][u]**2/12+(p['cg_m'][u]-centre[u])**2) for p in stock)
        start=list(centre);end=list(centre);start[axis]=lo[axis];end[axis]=hi[axis]
        if len(stock)==4:
            tposu=min(p['size_m'][u] for p in stock if abs(p['at_m'][u]+p['size_m'][u]-hi[u])<1e-7)
            tnegu=min(p['size_m'][u] for p in stock if abs(p['at_m'][u]-lo[u])<1e-7)
            tposw=min(p['size_m'][w] for p in stock if abs(p['at_m'][w]+p['size_m'][w]-hi[w])<1e-7)
            tnegw=min(p['size_m'][w] for p in stock if abs(p['at_m'][w]-lo[w])<1e-7)
            section=dict(kind='BOX',dimensions=[ext[u],ext[w],tposu,tposw,tnegu,tnegw])
        else:section=dict(kind='RECT',dimensions=[ext[u],ext[w]])
        members.append(dict(id=name,axis=axis,local_axis_1=u,start_m=start,end_m=end,length_m=length,
            area_m2=area,I_about_local_1_m4=Iu,I_about_local_2_m4=Iw,section=section,
            stock=stock,mass_kg=sum(p['mass_kg'] for p in stock),effective_joint=name.startswith('body-post-connection/')))
    return members


def post_connections(members):
    parts=[]
    posts=[m for m in members if m['axis']==2 and ('-post-' in m['id'])]
    for i,m in enumerate(posts):
        ps=m['stock'];x0=min(p['at_m'][0] for p in ps);x1=max(p['at_m'][0]+p['size_m'][0] for p in ps)
        y0=min(p['at_m'][1] for p in ps);y1=max(p['at_m'][1]+p['size_m'][1] for p in ps)
        top=m['start_m'][2]
        if abs(top-1.001)>1e-6:raise ValueError('Explicit post-floor datum required')
        # Foot is outside the existing sill (|y|>=1.19), so it does not fill the
        # floor-rib cavity or overlap retained panel/frame material.
        foot_y0=-1.19-(abs(y0)-1.19) if y1<0 else 1.19
        foot_width=abs(y0)-1.19 if y1<0 else y1-1.19
        parts.append(box(f'body-post-connection/{i}/foot',(x0,foot_y0,.7745),(x1-x0,foot_width,.020),system='post-base-connections'))
        parts.append(box(f'body-post-connection/{i}/riser',(x0,y0,.7945),(x1-x0,y1-y0,top-.7945),system='post-base-connections'))
    return parts


def contacts(members):
    rows=[]
    for i,a in enumerate(members):
        for j,b in enumerate(members[i+1:],i+1):
            points=[p for pa in a['stock'] for pb in b['stock'] if (p:=_contact(pa,pb)) is not None]
            if points:
                point=[sum(p[k] for p in points)/len(points) for k in range(3)]
                rows.append(dict(a=i,b=j,contact_m=point,finite_material_contacts=len(points)))
    return rows


def _components(members,cs):
    edges={i:set() for i in range(len(members))}
    for c in cs:edges[c['a']].add(c['b']);edges[c['b']].add(c['a'])
    components=[];unseen=set(edges)
    while unseen:
        start=min(unseen);seen={start};pending=[start]
        while pending:
            for j in edges[pending.pop()]:
                if j not in seen:seen.add(j);pending.append(j)
        unseen-=seen;components.append(sorted(seen))
    return components


def build(vehicle,root=ROOT):
    base=members_from_stock(vehicle['geometry_parts']);added=post_connections(base)
    variants=[]
    for name,extra in [('retained-frame-contact-only',[]),('counted-post-base-connections',added)]:
        ms=members_from_stock([*vehicle['geometry_parts'],*extra]);cs=contacts(ms);comps=_components(ms,cs)
        lower=next(i for i,m in enumerate(ms) if m['id'].startswith('wheel-underframe/sill/'))
        supported=next(c for c in comps if lower in c)
        roof=[i for i,m in enumerate(ms) if '/roof-longitudinal-' in m['id']]
        newmass=sum(p['mass_kg'] for p in extra)
        # A new physical alternative retains the unchanged installed accounts;
        # new joint stock is added conservatively, with no guessed subtraction.
        definition=dict(parent_candidate_id=vehicle['candidate_id'],variant=name,added_material=extra)
        variants.append(dict(alternative_id=identity(definition),name=name,physical_definition=definition,
            added_mass_kg=newmass,accounted_tare_kg_per_car=vehicle['mass']['accounted_tare_kg_per_car']+newmass,
            members=ms,contacts=cs,component_count=len(comps),supported_member_indices=supported,
            disconnected_member_ids=[ms[i]['id'] for i in range(len(ms)) if i not in supported],
            both_roof_chords_connected=all(i in supported for i in roof),
            added_material_parts=extra,existing_attachment_allowance_reconciled=False,
            applicability='No panel shear, glazing/doors or adhesive stiffness credited. Added blocks are manufacturable-stock proposals; welding/bolting, fatigue and thermal joints unqualified.',**FLAGS))
    value=dict(schema='osr-v06-body-frame-definition/1',**{k:vehicle[k] for k in IDS},variants=variants,
        assumptions=dict(E_Pa=69e9,nu=.33,density_kg_m3=2710.,frame_model='3D beam reduction of actual four-wall extrusion stock',
            joint='Rigid beam/section offsets at finite-area material contacts; upper-bound welded connection hypothesis',
            support='Ideal four vertical body bearers at the two bogie support planes; one axial and two transverse translation datums',
            load='Sprung body account = car minus6730kg bogie reference; applied to counted floor ribs, without extra selfweight. Whole-car reference is a separate conservative sensitivity',
            shell_stiffness_credited=False,buckling_fatigue_crash_and_joint_release_qualified=False),
        source_sha256={**vehicle['source_sha256'],**source_map(root,(PRODUCER,))},**FLAGS)
    value['evaluation_id']=identity(value);return value


def _mesh(variant,dx):
    members=variant['members'];cs=variant['contacts'];active=set(variant['supported_member_indices'])
    cuts={i:{0.,m['length_m']} for i,m in enumerate(members) if i in active}
    for c in cs:
        if c['a'] not in active or c['b'] not in active:continue
        for i in (c['a'],c['b']):cuts[i].add(min(members[i]['length_m'],max(0.,c['contact_m'][members[i]['axis']]-members[i]['start_m'][members[i]['axis']])))
    for i,m in enumerate(members):
        if i not in active:continue
        for j in range(1,ceil(m['length_m']/dx)):cuts[i].add(m['length_m']*j/ceil(m['length_m']/dx))
        if m['id'].startswith('wheel-underframe/sill/'):
            for x in (-6.4,6.4):cuts[i].add(x-m['start_m'][0])
        if '/floor-rib-' in m['id']:
            for y in (-.55,.55):cuts[i].add(y-m['start_m'][1])
    nodes={};points={};end_ids={};n=0;elements=[];eid=0
    for i in sorted(active):
        m=members[i];values=sorted({round(x,9) for x in cuts[i]});cuts[i]=values
        for u in values:
            p=list(m['start_m']);p[m['axis']]+=u;n+=1;nodes[n]=p;points[i,u]=n
        end_ids[i]=[points[i,u] for u in values]
        for a,b in zip(values,values[1:]):
            mid=(a+b)/2;p=list(m['start_m']);p[m['axis']]+=mid;n+=1;nodes[n]=p;eid+=1
            elements.append(dict(id=eid,member=i,nodes=[points[i,a],n,points[i,b]]))
    parent={i:i for i in nodes}
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def close_id(i,p):
        u=p[members[i]['axis']]-members[i]['start_m'][members[i]['axis']]
        return points[i,min(cuts[i],key=lambda s:abs(s-u))]
    for c in cs:
        if c['a'] not in active or c['b'] not in active:continue
        a=close_id(c['a'],c['contact_m']);b=close_id(c['b'],c['contact_m']);ra,rb=find(a),find(b)
        if ra!=rb:parent[max(ra,rb)]=min(ra,rb)
    equations=[]
    for node in nodes:
        ref=find(node)
        if ref==node:continue
        r=[nodes[node][j]-nodes[ref][j] for j in range(3)]
        for j in range(3):
            terms=[(node,j+1,1.),(ref,j+1,-1.)]
            # u_node = u_ref + theta_ref cross r.
            cross={0:[(5,-r[2]),(6,r[1])],1:[(6,-r[0]),(4,r[2])],2:[(4,-r[1]),(5,r[0])]}
            terms += [(ref,d,c) for d,c in cross[j] if abs(c)>1e-12]
            equations.append(terms)
        for dof in (4,5,6):equations.append([(node,dof,1.),(ref,dof,-1.)])
    supports=[]
    for i,m in enumerate(members):
        if i in active and m['id'].startswith('wheel-underframe/sill/'):
            for x in (-6.4,6.4):
                nid=points[i,min(cuts[i],key=lambda u:abs(m['start_m'][0]+u-x))]
                # Retain the actual beam node, which is not a dependent node at
                # these added cuts unless a physical bolster contact meets it.
                supports.append(find(nid))
    supports=sorted(set(supports))
    if len(supports)!=4:raise ValueError('Four independent body support points required')
    floor=[]
    for i,m in enumerate(members):
        if i in active and '/floor-rib-' in m['id']:
            ids=[]
            for y in (-.55,.55):
                nid=points[i,min(cuts[i],key=lambda u:abs(m['start_m'][1]+u-y))];ids.append(nid)
            floor.append((m['start_m'][0],ids))
    floor.sort()
    if len(floor)<10:raise ValueError('Actual floor rib load points required')
    return dict(nodes=nodes,elements=elements,equations=equations,supports=supports,floor=floor)


def deck(variant,mass_kg,dx=.5,*,asymmetric=False,braking=False,joint_factor=1.):
    mesh=_mesh(variant,dx);ms=variant['members'];lines=['*HEADING','V06 stock-derived body frame; no panel stiffness; rigid contact offsets','*NODE']
    lines += [str(i)+','+','.join(f'{x:.12g}' for x in p) for i,p in mesh['nodes'].items()]
    for i in sorted(set(e['member'] for e in mesh['elements'])):
        lines += [f'*ELEMENT,TYPE=B32R,ELSET=M{i}']
        lines += [str(e['id'])+','+','.join(map(str,e['nodes'])) for e in mesh['elements'] if e['member']==i]
    for name,factor in [('AL',1.),('JOINT',joint_factor)]:lines += [f'*MATERIAL,NAME={name}','*ELASTIC',f'{69e9*factor},0.33']
    for i in sorted(set(e['member'] for e in mesh['elements'])):
        m=ms[i];sec=m['section'];mat='JOINT' if m['effective_joint'] else 'AL';orient=[0.,0.,0.];orient[m['local_axis_1']]=1.
        lines += [f'*BEAM SECTION,ELSET=M{i},MATERIAL={mat},SECTION={sec["kind"]}',','.join(f'{v:.12g}' for v in sec['dimensions']),','.join(map(str,orient))]
    for eq in mesh['equations']:
        lines += ['*EQUATION',str(len(eq)),','.join(f'{n},{d},{c:.12g}' for n,d,c in eq)]
    lines += ['*BOUNDARY']
    for i in mesh['supports']:lines.append(f'{i},3,3')
    # Fix x/y at one end and y at the other; rotations stay free.
    support_sorted=sorted(mesh['supports'],key=lambda i:mesh['nodes'][i][0])
    lines += [f'{support_sorted[0]},1,2',f'{support_sorted[-1]},2,2']
    allnodes=sorted(mesh['nodes']);lines+=['*NSET,NSET=ALLN']
    lines += [','.join(map(str,allnodes[i:i+16])) for i in range(0,len(allnodes),16)]
    lines += ['*NSET,NSET=BEARERS',','.join(map(str,mesh['supports'])),'*STEP','*STATIC','*CLOAD']
    totalz=0.;totalx=0.;floor=mesh['floor']
    for k,(x,ids) in enumerate(floor):
        prev=-8.5 if k==0 else (floor[k-1][0]+x)/2
        nxt=8.5 if k==len(floor)-1 else (floor[k+1][0]+x)/2
        fraction=(nxt-prev)/17.
        for node,share in zip(ids,(.75,.25) if asymmetric else (.5,.5)):
            fz=-mass_kg*G*fraction*share;totalz+=fz;lines.append(f'{node},3,{fz:.12g}')
            if braking:
                fx=mass_kg*.6*fraction*share;totalx+=fx;lines.append(f'{node},1,{fx:.12g}')
    lines += ['*NODE PRINT,NSET=ALLN','U','*NODE PRINT,NSET=BEARERS','RF','*NODE FILE,OUTPUT=2D','U','*EL FILE,OUTPUT=2D','S','*END STEP','']
    return '\n'.join(lines),dict(nodes=len(mesh['nodes']),elements=len(mesh['elements']),support_nodes=mesh['supports'],total_vertical_load_N=totalz,total_longitudinal_load_N=totalx,
        boundary_conditions='Four ideal vertical body bearers, one x/y and one y translation datum; no rotational SPCs',effective_joint_modulus_fraction=joint_factor)


def _read_dat(path):
    text=Path(path).read_text();displacements=[];reactions=[];target=None
    for line in text.splitlines():
        if 'displacements' in line.lower():target=displacements
        elif 'forces' in line.lower():target=reactions
        fields=line.split()
        if target is not None and len(fields)==4 and fields[0].isdigit():
            try:target.append([int(fields[0]),*[float(x) for x in fields[1:]]])
            except ValueError:pass
    if not displacements:raise ValueError('No native frame displacements')
    if any(not isfinite(value) for row in displacements+reactions for value in row):raise ValueError('Nonfinite native frame response')
    return dict(maximum_vertical_displacement_m=max(abs(r[3]) for r in displacements),
        maximum_longitudinal_displacement_m=max(abs(r[1]) for r in displacements),
        maximum_lateral_displacement_m=max(abs(r[2]) for r in displacements),
        support_reaction_z_N=sum(r[3] for r in reactions),support_reaction_x_N=sum(r[1] for r in reactions),
        displaced_nodes=len(displacements),reaction_records=len(reactions))


def run_beam_benchmark(output):
    """NativeB32R BOX cantilever compared with the Euler slender-beam solution."""
    output=Path(output);output.mkdir()
    force=1000.;L=10.;b=.18;h=.35;t=.008;E=69e9
    expected=force*L**3/(3*E*(b*h**3-(b-2*t)*(h-2*t)**3)/12)
    results=[]
    for count in (10,20):
        folder=output/str(count);folder.mkdir();lines=['*HEADING','Independent hollow-box cantilever, N-m-Pa','*NODE']
        lines += [f'{i+1},{L*i/(2*count):.12g},0.,0.' for i in range(2*count+1)]
        lines += ['*ELEMENT,TYPE=B32R,ELSET=B']+[f'{i+1},{2*i+1},{2*i+2},{2*i+3}' for i in range(count)]
        lines += ['*MATERIAL,NAME=AL','*ELASTIC',f'{E},.33','*BEAM SECTION,ELSET=B,MATERIAL=AL,SECTION=BOX',f'{b},{h},{t},{t},{t},{t}','0.,1.,0.',
            '*BOUNDARY','1,1,6','*NSET,NSET=TIP',str(2*count+1),'*STEP','*STATIC','*CLOAD',f'{2*count+1},3,{-force}',
            '*NODE PRINT,NSET=TIP','U','*END STEP','']
        (folder/'cantilever.inp').write_text('\n'.join(lines))
        proc=subprocess.run(['/usr/bin/ccx','cantilever'],cwd=folder,capture_output=True,text=True,timeout=120,env={**os.environ,'OMP_NUM_THREADS':'1'})
        (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
        if proc.returncode or not (folder/'cantilever.dat').is_file():raise RuntimeError('Native beam benchmark failed')
        native=_read_dat(folder/'cantilever.dat')['maximum_vertical_displacement_m']
        results.append(dict(elements=count,deflection_m=native,Euler_m=expected,relative_error=(native-expected)/expected))
    return dict(schema='osr-v06-frame-beam-benchmark/1',cases=results,numerical_screen='pass' if abs(results[-1]['relative_error'])<.03 else 'fail',
        scope='Slender rectangular box beam only; independent section/orientation fixture, not validation of vehicle joints')

def run(output,vehicle,root=ROOT):
    output=Path(output);root=Path(root)
    if output.exists():raise ValueError('Fresh immutable body-frame directory required')
    output.mkdir(parents=True);definition=build(vehicle,root);before=definition['source_sha256'];(output/'definition.json').write_bytes(encoded(definition))
    cases=[];benchmark=run_beam_benchmark(output/'independent-beam-fixture')
    for variant in definition['variants']:
        # The current disconnected upperbody is reported, never silently tied.
        modes=[('normal-coarse','normal',.6,False,False,1.),('normal-fine','normal',.3,False,False,1.)]
        if variant['name']=='counted-post-base-connections':modes += [('empty','empty',.6,False,False,1.),('crowd','crowd',.6,False,False,1.),('asymmetric-braking','normal',.6,True,True,1.),('joint-flexibility','normal',.6,False,False,.1),('whole-car-conservative','whole-car',.6,False,False,1.)]
        for label,load,dx,asym,brake,jf in modes:
            extra=variant['added_mass_kg'];key={'normal':'accounted_cap_loaded_kg_per_car','empty':'accounted_tare_kg_per_car','crowd':'accounted_160_control_kg_per_car','whole-car':'accounted_cap_loaded_kg_per_car'}[load];mass=vehicle['mass'][key]+extra-(0. if load=='whole-car' else 6730.)
            folder=output/(variant['name']+'-'+label);folder.mkdir();raw,mesh=deck(variant,mass,dx,asymmetric=asym,braking=brake,joint_factor=jf);(folder/'frame.inp').write_text(raw)
            proc=subprocess.run(['/usr/bin/ccx','frame'],cwd=folder,capture_output=True,text=True,timeout=180,env={**os.environ,'OMP_NUM_THREADS':'1'})
            (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
            if proc.returncode or not (folder/'frame.dat').is_file():
                cases.append(dict(variant=variant['name'],case=label,execution='tool-error',returncode=proc.returncode,log_path=folder.relative_to(output).as_posix()));continue
            try:actual=_read_dat(folder/'frame.dat')
            except ValueError as error:
                cases.append(dict(variant=variant['name'],case=label,execution='numerical-error',reason=str(error),log_path=folder.relative_to(output).as_posix()));continue
            residual=actual['support_reaction_z_N']+mesh['total_vertical_load_N']
            actual.update(vertical_force_balance_residual_N=residual,vertical_force_balance_relative_error=abs(residual)/abs(mesh['total_vertical_load_N']))
            cases.append(dict(variant=variant['name'],alternative_id=variant['alternative_id'],case=label,loading=load,execution='completed',mesh=mesh,
                **actual,deflection_limit_m_hypothesis=.0256,necessary_deflection_screen='pass' if actual['maximum_vertical_displacement_m']<=.0256 else 'fail',
                numerical_validity='not yet independently confirmed',engineering_screen='unknown',physical_accepted=False))
    if build(vehicle,root)['source_sha256']!=before:raise ValueError('Body frame sources changed during native execution')
    refinement=[]
    for variant in definition['variants']:
        pair=[c for c in cases if c['variant']==variant['name'] and c['case'] in ('normal-coarse','normal-fine') and c['execution']=='completed']
        if len(pair)==2:
            coarse,fine=pair;relative=abs(coarse['maximum_vertical_displacement_m']-fine['maximum_vertical_displacement_m'])/fine['maximum_vertical_displacement_m']
            refinement.append(dict(variant=variant['name'],relative_deflection_change=relative,numerical_screen='pass' if relative<.02 and max(c['vertical_force_balance_relative_error'] for c in pair)<1e-4 else 'nonconverged-or-equilibrium-unconfirmed'))
    result=dict(schema='osr-v06-native-body-frame/1',**{k:vehicle[k] for k in IDS},definition_id=definition['evaluation_id'],
        execution='completed' if all(c['execution']=='completed' for c in cases) else 'completed-with-tool-errors',native_solver='CalculiX B32R box/rectangular 3D beams',
        cases=cases,refinement=refinement,independent_benchmark=benchmark,alternatives=[{k:v for k,v in a.items() if k not in ('members','contacts')} for a in definition['variants']],
        source_sha256=before,scope='Stock-derived frame and counted added post joints. Fully rigid contact-offset connections are an upper stiffness bound; panels excluded. Joint, buckling, fatigue, crash, flexible modes and equipped structure remain unqualified.',**FLAGS)
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result));m=dict(source_sha256=before,files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS);m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return result


def verify(output,vehicle,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Body frame receipt differs')
    if build(vehicle,root)['source_sha256']!=m['source_sha256']:raise ValueError('Body frame sources differ')
    if any(r[k]!=vehicle[k] for k in IDS):raise ValueError('Body frame parent candidate differs')
    for n,h in m['files_sha256'].items():
        if digest(output/n)!=h:raise ValueError('Body frame payload differs')
    if any(r.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Frame screen cannot grant physical release')
    return dict(verified=True,evaluation_id=r['evaluation_id'],cases=len(r['cases']),execution=r['execution'],**FLAGS)
