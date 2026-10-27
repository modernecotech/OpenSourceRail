"""Independent linear pin/axial graph method, never a vehicle frame solver.

Native T3D2 members carry axial force only. No moment stiffness, buckling,
joint stiffness, laminate, whole-car strength or physical release is inferred.
Numerical subdivisions constrain only artificial transverse midpoint motion.
"""
from pathlib import Path
from copy import deepcopy
from math import sqrt,isfinite
import os,resource,subprocess,time,re
import numpy as np
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import identity,digest,encoded

PRODUCER='engineering/design_search/grammar_structure.py'
SCOPE='Linear small-displacement, straight prismatic, pin-jointed axial graph; no bending, buckling, joint stiffness or whole-car qualification'
MISSING=['Compression buckling and member strength','Tube end cuts, joints, fasteners, hardpoints and joint stiffness/mass','Floor panels, concentrated floor loads, body attachment and eccentricity','Fatigue, modes, crash, fire and physical correlation','Complete installed vehicle mass and geometry/clearance qualification']


def _positive(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value) or value<=0:raise ValueError('Positive finite '+name+' required')
    return float(value)


def _validated(graph):
    g=deepcopy(graph);nodes=g.get('nodes',[]);members=g.get('members',[])
    if not 2<=len(nodes)<=256 or not 1<=len(members)<=2048:raise ValueError('Graph outside bounded method domain:2..256nodes/1..2048members')
    ids=[str(n['id']) for n in nodes]
    if len(set(ids))!=len(ids):raise ValueError('Unique physical node IDs required')
    coords={}
    for n,key in zip(nodes,ids):
        xyz=n.get('at_m',[])
        if len(xyz)!=3 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not isfinite(x) for x in xyz):raise ValueError('Finite3D node coordinates required')
        coords[key]=np.array(xyz,dtype=float)
    if len({str(m['id']) for m in members})!=len(members):raise ValueError('Unique physical member IDs required')
    materials=deepcopy(g.get('materials',{}));edges=set();stock=[]
    for m in members:
        a,b=str(m['start_node']),str(m['end_node']);s=m['section']
        if a not in coords or b not in coords or a==b:raise ValueError('Member endpoints must identify distinct declared nodes')
        edge=tuple(sorted((a,b)))
        if edge in edges:raise ValueError('Duplicate coincident graph members need explicit physical resolution')
        edges.add(edge);L=float(np.linalg.norm(coords[b]-coords[a]));_positive(L,'member length')
        width=_positive(s['width_m'],'section width');height=_positive(s['height_m'],'section height');wall=_positive(s['wall_m'],'section wall')
        if 2*wall>=min(width,height):raise ValueError('Positive hollow rectangular tube stock required')
        area=width*height-(width-2*wall)*(height-2*wall)
        if abs(_positive(s['area_m2'],'section area')-area)>max(1e-12,area*1e-8):raise ValueError('Declared area differs from actual four-wall tube stock')
        mid=str(s['material_id'])
        if mid in materials and m.get('material') is not None and m['material']!=materials[mid]:raise ValueError('Conflicting material hypotheses need separate material IDs')
        mat=materials.get(mid,m.get('material'))
        if not isinstance(mat,dict) or not mat.get('source_basis'):raise ValueError('Explicit material model and source basis required')
        E=_positive(mat['E_Pa'],'axial modulus');rho=mat.get('density_kg_m3')
        if rho is not None:rho=_positive(rho,'stock density')
        materials[mid]=mat;stock.append(dict(id=str(m['id']),start_node=a,end_node=b,section=deepcopy(s),material_id=mid,material=deepcopy(mat),length_m=L,area_m2=area,E_Pa=E,density_kg_m3=rho,stock_volume_m3=area*L,stock_mass_kg=area*L*rho if rho is not None else None,role=m.get('role','unspecified')))
    supports={key:set() for key in ids}
    for item in g.get('supports',[]):
        key=str(item['node_id']);dofs=item.get('dofs',[])
        if key not in supports or not dofs or any(isinstance(d,bool) or not isinstance(d,int) or d not in (1,2,3) for d in dofs):raise ValueError('Supported translational DOFs1..3 required')
        supports[key].update(dofs)
    loads={key:np.zeros(3) for key in ids}
    for item in g.get('loads',[]):
        key=str(item['node_id']);force=item.get('force_N',[])
        if key not in loads or len(force)!=3 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not isfinite(x) for x in force):raise ValueError('Finite nodal force vector required')
        loads[key]+=np.array(force)
    return g,ids,coords,stock,supports,loads


def _system(graph):
    g,ids,xyz,stock,supports,loads=_validated(graph);index={key:i for i,key in enumerate(ids)};B=np.zeros((len(stock),3*len(ids)));weights=[]
    for i,m in enumerate(stock):
        n=(xyz[m['end_node']]-xyz[m['start_node']])/m['length_m'];a=3*index[m['start_node']];b=3*index[m['end_node']];B[i,a:a+3]=-n;B[i,b:b+3]=n;weights.append(m['E_Pa']*m['area_m2']/m['length_m'])
    fixed=sorted(3*index[key]+d-1 for key,ds in supports.items() for d in ds);free=sorted(set(range(3*len(ids)))-set(fixed));F=np.concatenate([loads[key] for key in ids]);K=B.T@(np.array(weights)[:,None]*B)
    return dict(graph=g,ids=ids,xyz=xyz,stock=stock,supports=supports,loads=loads,B=B,K=K,F=F,fixed=fixed,free=free)


def _physical_id(system):
    return identity(dict(nodes=[dict(id=key,at_m=system['xyz'][key].tolist()) for key in system['ids']],members=[{k:m[k] for k in ('id','start_node','end_node','section','material_id','role')} for m in system['stock']]))


def diagnose_rigidity(graph):
    s=_system(graph);free=s['free'];A=s['B'][:,free];u,sv,vh=np.linalg.svd(A,full_matrices=True);tol=max(1e-11,(float(sv[0]) if len(sv) else 1.)*1e-10);rank=int(sum(sv>tol));mechanisms=len(free)-rank;null=vh[rank:].T;projection=float(np.linalg.norm(null.T@s['F'][free])) if mechanisms else 0.
    vectors=[]
    for j in range(min(mechanisms,6)):
        full=np.zeros(len(s['F']));full[free]=null[:,j];i=int(np.argmax(abs(full)));vectors.append(dict(maximum_component_node=s['ids'][i//3],dof=i%3+1,normalised_vector=full.tolist()))
    density_unknown=[m['id'] for m in s['stock'] if m['stock_mass_kg'] is None];known=sum(m['stock_mass_kg'] for m in s['stock'] if m['stock_mass_kg'] is not None)
    return dict(physical_graph_id=_physical_id(s),input_graph_id=identity(graph),node_count=len(s['ids']),member_count=len(s['stock']),free_dofs=len(free),compatibility_rank=rank,mechanism_count=mechanisms,rank_tolerance=tol,singular_values=sv.tolist(),load_projection_onto_mechanisms_N=projection,mechanism_vectors=vectors,
        necessary_rigidity_screen='pass' if mechanisms==0 else 'fail',counted_member_stock_mass_kg=None if density_unknown else known,known_member_stock_subtotal_kg=known,unknown_density_member_ids=density_unknown,unknown_joint_hardware_mass_kg=None,
        minimum_member_length_to_max_section_dimension=min(m['length_m']/max(m['section']['width_m'],m['section']['height_m']) for m in s['stock']),short_member_ids=[m['id'] for m in s['stock'] if m['length_m']/max(m['section']['width_m'],m['section']['height_m'])<10],
        stock_scope='Gross untrimmed prismatic tube centreline lengths; joint/miter/cross-section-roll and complete installed mass unresolved',model_scope=SCOPE,**FLAGS)


def linear_reference(graph):
    """Direct compatibility/stiffness assembly, independent of native parser."""
    s=_system(graph);d=diagnose_rigidity(graph)
    if d['mechanism_count']:raise ValueError('Necessary rigidity failure; no unique pin-graph solution')
    U=np.zeros(len(s['F']));free=s['free']
    if free:U[free]=np.linalg.solve(s['K'][np.ix_(free,free)],s['F'][free])
    R=s['K']@U-s['F'];N=np.array([m['E_Pa']*m['area_m2']/m['length_m'] for m in s['stock']])*(s['B']@U)
    return dict(displacements_m={key:U[3*i:3*i+3].tolist() for i,key in enumerate(s['ids'])},reactions_N={key:R[3*i:3*i+3].tolist() for i,key in enumerate(s['ids'])},member_axial_forces_N={m['id']:float(n) for m,n in zip(s['stock'],N)},strain_energy_J=float(.5*U@s['K']@U),external_work_J=float(.5*s['F']@U))


def deck(graph,subdivisions=1):
    if isinstance(subdivisions,bool) or not isinstance(subdivisions,int) or subdivisions not in (1,2,4):raise ValueError('Bounded axial subdivisions1,2,4 required')
    s=_system(graph);diagnostic=diagnose_rigidity(graph)
    if diagnostic['mechanism_count']:raise ValueError('Graph mechanism refused before native solve')
    ns={i+1:s['xyz'][key].tolist() for i,key in enumerate(s['ids'])};base={key:i+1 for i,key in enumerate(s['ids'])};es=[];eqs=[];groups=[]
    for j,m in enumerate(s['stock']):
        start,end=base[m['start_node']],base[m['end_node']];a,b=s['xyz'][m['start_node']],s['xyz'][m['end_node']];direction=(b-a)/m['length_m'];axis=int(np.argmax(abs(direction)));chain=[start]
        for i in range(1,subdivisions):
            alpha=i/subdivisions;n=len(ns)+1;ns[n]=((1-alpha)*a+alpha*b).tolist();chain.append(n)
            for d in range(3):
                if d==axis:continue
                ratio=direction[d]/direction[axis];terms=[(n,d+1,1.),(start,d+1,-(1-alpha)),(end,d+1,-alpha)]
                if abs(ratio)>1e-14:terms += [(n,axis+1,-ratio),(start,axis+1,(1-alpha)*ratio),(end,axis+1,alpha*ratio)]
                eqs.append(terms)
        chain.append(end);ids=[]
        for a,b in zip(chain,chain[1:]):ids.append(len(es)+1);es.append((a,b))
        groups.append((m,ids))
    lines=['*HEADING','Independent pin-jointed axial graph; SI N-m-Pa-kg','*NODE']+[str(n)+','+','.join(f'{v:.14g}' for v in xyz) for n,xyz in ns.items()]
    for j,(m,ids) in enumerate(groups):
        lines.append(f'*ELEMENT,TYPE=T3D2,ELSET=M{j}');lines += [f'{i},{es[i-1][0]},{es[i-1][1]}' for i in ids]
        lines += [f'*MATERIAL,NAME=MAT{j}','*ELASTIC',f'{m["E_Pa"]:.14g},0.']
        if m['density_kg_m3'] is not None:lines += ['*DENSITY',f'{m["density_kg_m3"]:.14g}']
        lines += [f'*SOLID SECTION,ELSET=M{j},MATERIAL=MAT{j}',f'{m["area_m2"]:.14g}']
    lines+=['*ELSET,ELSET=ALLMEMBERS'];names=[f'M{i}' for i in range(len(groups))];lines += [','.join(names[i:i+16]) for i in range(0,len(names),16)]
    for eq in eqs:lines += ['*EQUATION',str(len(eq)),','.join(f'{n},{d},{c:.14g}' for n,d,c in eq)]
    lines += ['*BOUNDARY']+[f'{base[key]},{d},{d}' for key,ds in s['supports'].items() for d in sorted(ds)]+['*NSET,NSET=OUTPUT']
    ids=sorted(ns);lines += [','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]
    supports=[base[key] for key,ds in s['supports'].items() if ds];lines += ['*NSET,NSET=SUPPORTS']+[','.join(map(str,supports[i:i+16])) for i in range(0,len(supports),16)]+['*STEP','*STATIC','*CLOAD']
    lines += [f'{base[key]},{d+1},{force:.14g}' for key,vector in s['loads'].items() for d,force in enumerate(vector) if force]
    lines += ['*NODE PRINT,NSET=OUTPUT','U','*NODE PRINT,NSET=SUPPORTS','RF','*EL PRINT,ELSET=ALLMEMBERS,TOTALS=ONLY','ELSE','*END STEP','']
    return '\n'.join(lines),dict(graph_diagnostic=diagnostic,nodes=ns,original_node_numbers=base,subdivisions=subdivisions,elements=len(es),transverse_interpolation_equations=len(eqs),
        interpolation_scope='Only artificial midpoint transverse motion follows straight-member interpolation; axial displacement remains free. Subdivision invariance is not3D mesh/buckling convergence',model_scope=SCOPE)


def _parse(path):
    U={};RF={};active=None;energy=None;want_energy=False
    for line in Path(path).read_text().splitlines():
        low=line.lower();f=line.split()
        if 'displacements' in low:active=U
        elif 'forces' in low:active=RF
        elif 'total internal energy' in low:active=None;want_energy=True
        elif want_energy and len(f)==1:
            try:energy=float(f[0]);want_energy=False
            except ValueError:pass
        elif active is not None and len(f)==4 and f[0].isdigit():active[int(f[0])]=list(map(float,f[1:]))
    if not U or energy is None or not isfinite(energy) or any(not isfinite(x) for v in list(U.values())+list(RF.values()) for x in v):raise ValueError('Missing/nonfinite native displacement/reaction/energy')
    return U,RF,energy


def analyse(graph,definition,path):
    s=_system(graph);reference=linear_reference(graph);U,RF,energy=_parse(path);numbers=definition['original_node_numbers'];native={key:np.array(U[numbers[key]]) for key in s['ids']};reaction={}
    # CalculiX RF is reaction PLUS applied concentrated load at the node.
    # Recover reactions explicitly, including loads at supported nodes.
    for key,ds in s['supports'].items():
        if ds:reaction[key]=np.array(RF[numbers[key]])-s['loads'][key]
    residual_force=sum(reaction.values(),np.zeros(3))+sum(s['loads'].values(),np.zeros(3));residual_moment=sum((np.cross(s['xyz'][key],v) for key,v in reaction.items()),np.zeros(3))+sum((np.cross(s['xyz'][key],v) for key,v in s['loads'].items()),np.zeros(3))
    force_scale=max(sum(float(np.linalg.norm(f)) for f in s['loads'].values()),1.);length_scale=max(float(np.linalg.norm(np.ptp(np.array(list(s['xyz'].values())),axis=0))),1e-6);force_error=float(max(abs(residual_force)))/force_scale;moment_error=float(max(abs(residual_moment)))/(force_scale*length_scale)
    work=.5*sum(float(s['loads'][key]@native[key]) for key in s['ids']);energy_error=abs(work-energy)/max(abs(work),1e-30);refscale=max(max(np.linalg.norm(u) for u in reference['displacements_m'].values()),1e-12);reference_error=max(float(np.linalg.norm(native[key]-reference['displacements_m'][key])) for key in s['ids'])/refscale
    axial={};strains=[];relative_motion=[]
    for m in s['stock']:
        relative=native[m['end_node']]-native[m['start_node']];n=(s['xyz'][m['end_node']]-s['xyz'][m['start_node']])/m['length_m'];strain=float(n@relative)/m['length_m'];strains.append(abs(strain));relative_motion.append(float(np.linalg.norm(relative))/m['length_m']);axial[m['id']]=m['E_Pa']*m['area_m2']*strain
    maximum=max(float(np.linalg.norm(v)) for v in native.values());linear_ratio=max(relative_motion);valid=max(force_error,moment_error,energy_error,reference_error)<1e-4 and linear_ratio<.01
    return dict(execution='completed',numerical_validity='verified_axial_method' if valid else 'outside_linear_domain' if linear_ratio>=.01 else 'unknown',engineering_screen='unknown',displacements_m={k:v.tolist() for k,v in native.items()},reactions_N={k:v.tolist() for k,v in reaction.items()},member_axial_forces_N=axial,
        maximum_displacement_m=maximum,maximum_abs_axial_strain=max(strains),maximum_member_relative_displacement_to_length=linear_ratio,force_residual_N=residual_force.tolist(),moment_residual_Nm=residual_moment.tolist(),force_relative_residual=force_error,moment_relative_residual=moment_error,force_scale_N=force_scale,moment_scale_Nm=force_scale*length_scale,
        native_strain_energy_J=energy,external_work_J=work,energy_relative_residual=energy_error,independent_axial_reference=reference,reference_displacement_relative_error=reference_error,model_scope=SCOPE)


def run(graph,output,*,subdivisions=1,root=ROOT,memory_mb=2048,timeout_s=45):
    if isinstance(memory_mb,bool) or not isinstance(memory_mb,int) or memory_mb not in (1024,2048) or timeout_s not in (30,45):raise ValueError('Bounded axial resources1024/2048MiB and30/45seconds required')
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh immutable graph package required')
    source=digest(__file__);sources={**graph.get('source_sha256',{}),PRODUCER:source}
    for name,expected in sources.items():
        if digest(Path(root)/name)!=expected:raise ValueError('Graph source mismatch: '+name)
    diagnostic=diagnose_rigidity(graph);output.mkdir(parents=True);(output/'graph.json').write_bytes(encoded(graph));(output/'rigidity.json').write_bytes(encoded(diagnostic));start=time.monotonic();tool=None
    if diagnostic['mechanism_count']:result=dict(execution='not_run_rigidity_failure',numerical_validity='not_evaluated',engineering_screen='necessary_rigidity_fail',native_jobs_used=0)
    else:
        raw,definition=deck(graph,subdivisions);(output/'graph.inp').write_text(raw);(output/'definition.json').write_bytes(encoded(definition));ccx='/usr/bin/ccx';finite=[n for n in resource.getrlimit(resource.RLIMIT_AS) if n!=resource.RLIM_INFINITY];cap=min([memory_mb*1024**2,*finite]);tool=dict(ccx_path=ccx,ccx_sha256=digest(ccx),OMP_threads=1,requested_memory_mb=memory_mb,RLIMIT_AS_bytes=cap,timeout_s=timeout_s)
        def bounded():resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
        try:
            proc=subprocess.run([ccx,'graph'],cwd=output,capture_output=True,timeout=timeout_s,preexec_fn=bounded,env={**os.environ,'OMP_NUM_THREADS':'1'});(output/'stdout.log').write_bytes(proc.stdout);(output/'stderr.log').write_bytes(proc.stderr);result=dict(execution='tool_error',returncode=proc.returncode,native_jobs_used=1)
            if proc.returncode==0:result.update(analyse(graph,definition,output/'graph.dat'))
        except subprocess.TimeoutExpired as e:
            (output/'stdout.log').write_bytes(e.stdout or b'');(output/'stderr.log').write_bytes(e.stderr or b'');result=dict(execution='interrupted',reason='bounded native timeout',native_jobs_used=1)
        except (OSError,ValueError,KeyError,subprocess.SubprocessError) as e:result=dict(execution='tool_error',reason=str(e),native_jobs_used=1)
        if digest(ccx)!=tool['ccx_sha256']:raise ValueError('Axial solver binary changed during execution')
    for name,expected in sources.items():
        if digest(Path(root)/name)!=expected:raise ValueError('Graph source changed: '+name)
    if digest(__file__)!=source:raise ValueError('Imported axial producer differs from declared source')
    result.update(schema='osr-native-axial-graph/1',candidate_id=graph.get('candidate_id'),physical_graph_id=diagnostic['physical_graph_id'],input_graph_id=identity(graph),subdivisions=subdivisions,diagnostic=diagnostic,runtime_s=time.monotonic()-start,source_sha256=sources,tool=tool,missing_gates=MISSING,**FLAGS);result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result));manifest=dict(evaluation_id=result['evaluation_id'],physical_graph_id=diagnostic['physical_graph_id'],source_sha256=sources,tool=tool,files_sha256={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()},**FLAGS);manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return result


def benchmark_plan():
    section=dict(width_m=.04,height_m=.04,wall_m=.002,area_m2=.04**2-.036**2,material_id='synthetic-al');mat=dict(E_Pa=69e9,density_kg_m3=2710.,source_basis='Declared synthetic aluminium method fixture, not a supplier allowable')
    def member(name,a,b):return dict(id=name,start_node=a,end_node=b,section=deepcopy(section),role='method-fixture')
    axial=dict(nodes=[dict(id='fixed',at_m=[0.,0.,0.]),dict(id='tip',at_m=[2.,0.,0.])],members=[member('bar','fixed','tip')],materials={'synthetic-al':mat},supports=[dict(node_id='fixed',dofs=[1,2,3]),dict(node_id='tip',dofs=[2,3])],loads=[dict(node_id='tip',force_N=[1000.,0.,0.]),dict(node_id='fixed',force_N=[200.,0.,0.])])
    tetra=dict(nodes=[dict(id=str(i),at_m=p) for i,p in enumerate(([1.,0.,0.],[-.5,sqrt(3)/2,0.],[-.5,-sqrt(3)/2,0.],[0.,0.,1.]))],members=[member(str(i),str(i),'3') for i in range(3)],materials={'synthetic-al':mat},supports=[dict(node_id=str(i),dofs=[1,2,3]) for i in range(3)],loads=[dict(node_id='3',force_N=[0.,0.,-1000.])])
    mechanism=dict(nodes=[dict(id=str(i),at_m=p) for i,p in enumerate(([0.,0.,0.],[1.,0.,0.],[0.,0.,1.],[1.,0.,1.]))],members=[member(str(i),str(a),str(b)) for i,(a,b) in enumerate(((0,1),(0,2),(1,3),(2,3)))],materials={'synthetic-al':mat},supports=[dict(node_id='0',dofs=[1,2,3]),dict(node_id='1',dofs=[1,2,3]),dict(node_id='2',dofs=[2]),dict(node_id='3',dofs=[2])],loads=[dict(node_id='3',force_N=[100.,0.,0.])])
    EA=mat['E_Pa']*section['area_m2']
    return dict(native_jobs=[dict(id=name+'-s'+str(n),graph=deepcopy(g),subdivisions=n) for name,g in [('axial',axial),('tripod',tetra)] for n in (1,2)],necessary_controls=[dict(id='unbraced-mechanism',graph=mechanism)],
        analytical_checks=dict(axial_tip_x_m=1000*2/EA,axial_fixed_reaction_x_N=-1200.,tripod_tip_z_m=-1000*2*sqrt(2)/(3*EA)),maximum_native_jobs=4,scope=SCOPE,**FLAGS)
