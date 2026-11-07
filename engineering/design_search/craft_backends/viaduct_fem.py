"""Exact imported-CAD elastic viaduct research; no bridge resistance approval.

The optional Gmsh route imports the exact SolidCraft STEP and fragments touching
prisms into a bonded continuum. That is a declared evaluation hypothesis, not a
claim that joints, concrete cracking, tendons or bearings have been engineered.
"""
from copy import deepcopy
from math import fsum,isfinite,sqrt
from pathlib import Path
import json,os,platform,resource,shutil,signal,subprocess,time
from . import native,identity,FLAGS
from .fieldcraft import batch_results
from .. import civil_shape_geometry as geometry,civil_shape_mechanics as mechanics,civil_shape_portfolio as portfolio,model_cost

SCREENS=dict(force_relative=1e-5,moment_relative=1e-5,displacement_refinement_relative=.05,
             cross_solver_displacement_relative=.02,positive_jacobians=True)
SOURCE='engineering/design_search/craft_backends/viaduct_fem.py'
ROOT=Path(__file__).resolve().parents[3]


def sources(root=ROOT):
    names=(SOURCE,'engineering/design_search/craft_backends/native.py','engineering/design_search/craft_backends/fieldcraft.py',
           'engineering/design_search/craft_backends/__init__.py','engineering/design_search/craft_backends/cases.py',
           'engineering/design_search/craft_backends/tools.json','engineering/design_search/civil_shape_geometry.py',
           'engineering/design_search/civil_shape_mechanics.py','engineering/design_search/civil_shape_portfolio.py','engineering/station_rail/common.py')
    return {n:native.digest(Path(root)/n) for n in names}


def prepare(case,cad_artifact,load_case='crowd_control',*,root=ROOT):
    """Authenticate canonical geometry, exact CAD bytes, common loads and reserves."""
    if case.get('case_definition_id')!=identity({k:v for k,v in case.items() if k!='case_definition_id'}):raise ValueError('Case seal differs')
    p=case['physical_definition'];canonical=geometry.generate(case['family'],case['profile'])
    if p!=canonical or case['candidate_id']!=p['candidate_id']:raise ValueError('Canonical physical candidate differs')
    projection=dict(schema='osr-civil-cad-geometry/1',units='m',entities=[{k:e[k] for k in ('id','shape','geometry','material')} for e in case['entities']])
    if identity(projection)!=case['component_geometry_id']:raise ValueError('CAD component geometry differs')
    expected=[]
    for cell in p['cells']:
        for s in cell['sections']:
            expected.append(dict(id=cell['id']+'/'+s['id'],shape='profile',geometry=dict(at_m=[cell['x_start_m'],0.,0.],
                points_yz_m=s['polygon_yz_m'],length_m=cell['x_end_m']-cell['x_start_m']),material=s['material']))
    if projection['entities']!=expected:raise ValueError('CAD entities are not the exact physical geometry')
    if p['span_m']!=20 or p['family'] not in ('reference_box','folded_plate') or p['profile']!='reference':raise ValueError('Bounded 20m reference/folded pilot only')
    if any(s['material']!='research_concrete' for c in p['cells'] for s in c['sections']):raise ValueError('Single concrete continuum hypothesis only')
    for k in ('candidate_id','component_geometry_id'):
        if cad_artifact.get(k)!=case[k]:raise ValueError('Mixed CAD artifact '+k)
    cad=Path(cad_artifact['step_path']).resolve()
    if cad.is_symlink() or native.digest(cad)!=cad_artifact['step_sha256']:raise ValueError('Exact STEP bytes differ')
    context=mechanics.load_context(root);mechanics._context_binding(context,root)
    load=next((v for v in context['cases'] if v['name']==load_case),None)
    if load is None:raise ValueError('Named common selected load required')
    pose=mechanics._representative_pose(20.,tuple(load['offsets_m']),load['force_N_per_full_axle'])
    q=geometry.quantities(p);cost=portfolio.estimate(p,q,portfolio.specification(root),model_cost.assumptions(root))
    base=next(v for v in cost['cases'] if v['case']=='base')
    extra=base['accounted_delivery_mass_kg']-q['total_nominal_stock_mass_kg']
    if extra<0:raise ValueError('Negative non-CAD reserve mass')
    spec=dict(schema='osr-viaduct-fem-input/1',candidate_id=p['candidate_id'],component_geometry_id=case['component_geometry_id'],
        case_definition_id=case['case_definition_id'],physical_definition=deepcopy(p),cad_artifact=deepcopy(cad_artifact),
        units='m-kg-s-N-Pa',load_context=deepcopy(context),load_case=deepcopy(load),live_pose=pose,
        nominal_quantity=deepcopy(q),cost_estimate=cost,superimposed_mass_kg=extra,
        material_hypothesis=dict(young_Pa=35e9,poisson=.2,density_kg_m3=2500.,scope='Uncracked homogeneous isotropic research concrete; no reinforcement/prestress strength or stiffness credit'),
        rail_patch_hypothesis=dict(centres_y_m=[-.6,.6],length_x_m=.3,width_y_m=.2,full_axle_split=[.5,.5],
          scope='Declared load spreading patches, not verified rail/fastener interface; full axle includes dynamic factor once'),
        support_hypothesis=dict(bottom_patch_x_m=[[0.,.3],[19.7,20.]],patch_y_m=[-.25,.25],
          scope='Vertical displacement restrained on bottom bearing patches; one axial/lateral point restraint and one second lateral point restraint remove rigid modes; actual bearings/foundations unresolved'),
        deadload_hypothesis='Exact nominal CAD continuum selfweight; base cost-model non-CAD mass uniformly on deck as gravity only, not stiffness or located installed equipment',
        screens=deepcopy(SCREENS),**FLAGS)
    spec['input_id']=identity(spec);return spec


def bounded(argv,folder,*,read_roots=(),timeout_s=120):
    """One native process with recorded bwrap scope and per-process 2GiB AS."""
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    if not shutil.which('bwrap'):raise ValueError('Bubblewrap required; no unconfined fallback')
    cmd=['/usr/bin/time','-f','{"peak_rss_kib":%M,"wall_s":%e,"exit":%x}','-o',str(folder/'usage.json'),
         'bwrap','--die-with-parent','--unshare-net','--ro-bind','/','/','--tmpfs','/home','--tmpfs','/root','--dev','/dev']
    for p in read_roots:cmd+=['--ro-bind',str(Path(p).resolve()),str(Path(p).resolve())]
    cmd+=['--bind',str(folder),str(folder),'--chdir',str(folder),'--',*map(str,argv)]
    request=dict(argv=list(map(str,argv)),wrapper_argv=cmd,resources=dict(timeout_s=timeout_s,memory_mb=2048,single_thread=True),
      executable_sha256=native.digest(argv[0]),scope='Read-only host, hidden home, no network, private write directory; POSIX per-process address space, not aggregate cgroup',**FLAGS)
    native.write(folder/'invocation.json',request)
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,)*2);resource.setrlimit(resource.RLIMIT_CPU,(timeout_s+1,timeout_s+2));resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
    env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','RAYON_NUM_THREADS':'1','CCX_NPROC_RESULTS':'1','CCX_NPROC_EQUATION_SOLVER':'1'}
    started=time.monotonic();timed=False
    with (folder/'stdout.log').open('wb') as out,(folder/'stderr.log').open('wb') as err:
        p=subprocess.Popen(cmd,stdout=out,stderr=err,env=env,preexec_fn=limits,start_new_session=True)
        try:code=p.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);code=p.wait();timed=True
    r=dict(state='timeout' if timed else 'executed' if code==0 else 'failed',returncode=code,elapsed_s=time.monotonic()-started,invocation_id=identity(request),
        isolation_established_for_successful_execution=code==0,**FLAGS)
    if (folder/'usage.json').is_file():
        try:r['usage']=json.loads((folder/'usage.json').read_text().splitlines()[-1])
        except (ValueError,IndexError):pass
    native.write(folder/'execution.json',r);return r


GMSH_WORKER=r'''
import gmsh,json,sys,math
from pathlib import Path
request=json.loads(Path(sys.argv[1]).read_text());gmsh.initialize();gmsh.option.setNumber('General.NumThreads',1)
gmsh.option.setNumber('General.Terminal',1);gmsh.option.setNumber('Geometry.OCCTargetUnit','M')
v=gmsh.model.occ.importShapes(request['step']);gmsh.model.occ.synchronize()
original=sum(gmsh.model.occ.getMass(3,t) for d,t in v if d==3)
# Fragment exact imported CAD into one conformal, perfectly bonded continuum.
vol=[v for v in gmsh.model.getEntities(3)]
if len(vol)>1:gmsh.model.occ.fragment(vol[:1],vol[1:]);gmsh.model.occ.synchronize()
volume=sum(gmsh.model.occ.getMass(3,t) for d,t in gmsh.model.getEntities(3))
if abs(volume-request['volume'])>1e-6*request['volume']:raise ValueError('STEP volume differs from canonical SI stock')
# An explicit observation point lies on the actual deck face, not an invented CAD solid.
pt=gmsh.model.occ.addPoint(10.,0.,0.);gmsh.model.occ.synchronize()
top=[t for d,t in gmsh.model.getEntities(2) if abs(gmsh.model.occ.getCenterOfMass(d,t)[2])<1e-8]
inside=[t for t in top if gmsh.model.isInside(2,t,[10.,0.,0.])]
if len(inside)!=1:raise ValueError('Unique canonical top-deck observation surface required')
gmsh.model.mesh.embed(0,[pt],2,inside[0])
gmsh.option.setNumber('Mesh.MeshSizeMin',request['size']);gmsh.option.setNumber('Mesh.MeshSizeMax',request['size'])
gmsh.option.setNumber('Mesh.Algorithm',6);gmsh.option.setNumber('Mesh.Algorithm3D',1);gmsh.model.mesh.generate(3)
gmsh.option.setNumber('Mesh.SecondOrderLinear',1);gmsh.model.mesh.setOrder(2)
# Straight-sided planar prisms need no curved midside projection.
nt,coords,_=gmsh.model.mesh.getNodes();nodes={str(int(n)):list(map(float,coords[3*i:3*i+3])) for i,n in enumerate(nt)}
types,tags,conn=gmsh.model.mesh.getElements(3);elements={}
for typ,ids,links in zip(types,tags,conn):
 if int(typ)!=11:raise ValueError('Only actual quadratic tetrahedra admitted')
 for i,n in enumerate(ids):elements[str(int(n))]=[int(links[10*i+j]) for j in (0,1,2,3,4,5,6,7,9,8)]
faces=[]
for surf in top:
 types,tags,conn=gmsh.model.mesh.getElements(2,surf)
 for typ,ids,links in zip(types,tags,conn):
  if int(typ)!=9:raise ValueError('Quadratic deck triangles required')
  faces += [list(map(int,links[6*i:6*i+6])) for i in range(len(ids))]
ids=list(map(int,elements));qualities=list(map(float,gmsh.model.mesh.getElementQualities(ids,'minSJ')))
if not qualities or min(qualities)<=0:raise ValueError('Nonpositive Jacobian quality')
Path(request['output']).write_text(json.dumps(dict(nodes=nodes,elements=elements,top_faces=faces,element_type='tet10',gmsh_version=gmsh.__version__,
 original_imported_volume_m3=original,fused_volume_m3=volume,min_scaled_jacobian=min(qualities),geometry_route='Gmsh/OpenCASCADE exact SolidCraft STEP import, fragments touching stock, quadratic tetrahedra; perfect bond hypothesis'))+'\n')
gmsh.write(request['msh']);gmsh.finalize()
'''


def mesh(spec,level,output,*,python='/home/hayder/Documents/OpenSourceRail/.venv/bin/python'):
    if level not in ('coarse','fine'):raise ValueError('Predeclared coarse/fine levels only')
    folder=Path(output).resolve();folder.mkdir(parents=True,exist_ok=False)
    step=folder/'exact-solidcraft.step';shutil.copyfile(spec['cad_artifact']['step_path'],step)
    if native.digest(step)!=spec['cad_artifact']['step_sha256']:raise ValueError('Staged CAD differs')
    worker=folder/'gmsh-worker.py';worker.write_text(GMSH_WORKER)
    req=dict(step=str(step),volume=spec['nominal_quantity']['total_nominal_volume_m3'],size=.3 if level=='coarse' else .2,output=str(folder/'native'/'imported-mesh.json'),msh=str(folder/'native'/'imported.msh'))
    native.write(folder/'request.json',req)
    envroot=Path(python).parent.parent
    execution=bounded([str(Path(python)),str(worker),str(folder/'request.json')],folder/'native',read_roots=(folder,envroot,Path(python).resolve().parent.parent))
    if execution['state']!='executed':raise ValueError('Exact-CAD mesh execution failed; retained '+str(folder))
    model=json.loads((folder/'native'/'imported-mesh.json').read_text());model.update(level=level,candidate_id=spec['candidate_id'],component_geometry_id=spec['component_geometry_id'],input_id=spec['input_id'])
    model=load_model(spec,model);model['mesh_id']=identity(model);native.write(folder/'mesh.json',model);return model


def _clip(poly,axis,bound,greater):
    out=[]
    for a,b in zip(poly[-1:]+poly[:-1],poly):
        ia=(a[axis]>=bound) if greater else (a[axis]<=bound);ib=(b[axis]>=bound) if greater else (b[axis]<=bound)
        if ia!=ib:
            t=(bound-a[axis])/(b[axis]-a[axis]);out.append([a[j]+t*(b[j]-a[j]) for j in range(2)])
        if ib:out.append(b)
    return out


def surface_forces(model,rect,total):
    """Consistent quadratic triangle traction; exact clipped quadratic quadrature."""
    result={};area_total=0.;N=model['nodes'];xmin,xmax,ymin,ymax=rect
    for face in model['top_faces']:
        xyz=[N[str(n)][:2] for n in face[:3]];p=xyz
        for axis,bound,greater in ((0,xmin,True),(0,xmax,False),(1,ymin,True),(1,ymax,False)):p=_clip(p,axis,bound,greater)
        if len(p)<3:continue
        a,b,c=xyz;det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        if abs(det)<1e-14:raise ValueError('Degenerate deck triangle')
        for q,r in zip(p[1:-1],p[2:]):
            u=p[0];area=abs((q[0]-u[0])*(r[1]-u[1])-(q[1]-u[1])*(r[0]-u[0]))/2;area_total+=area
            for weights in ((2/3,1/6,1/6),(1/6,2/3,1/6),(1/6,1/6,2/3)):
                x,y=[sum(w*v[d] for w,v in zip(weights,(u,q,r))) for d in range(2)]
                l2=((x-a[0])*(c[1]-a[1])-(y-a[1])*(c[0]-a[0]))/det
                l3=((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]))/det;l1=1-l2-l3
                shape=(l1*(2*l1-1),l2*(2*l2-1),l3*(2*l3-1),4*l1*l2,4*l2*l3,4*l3*l1)
                for n,v in zip(face,shape):result[n]=result.get(n,0.)+v*area/3
    expected=(xmax-xmin)*(ymax-ymin)
    if abs(area_total-expected)>1e-6*expected:raise ValueError('Load patch is not completely covered by actual CAD deck')
    return {n:-total*v/area_total for n,v in result.items()}


def load_model(spec,model):
    import numpy as np
    validate_elements(model)
    nodes=model['nodes'];forces={int(n):0. for n in nodes};volume=0.
    for e in model['elements'].values():
        p=np.array([nodes[str(n)] for n in e[:4]]);v=abs(float(np.linalg.det((p[1:]-p[0]).T)))/6;volume+=v
        for n,w in zip(e,[-1/20]*4+[1/5]*6):forces[n]-=2500.*9.80665*v*w
    nominal=spec['nominal_quantity']['total_nominal_volume_m3']
    if abs(volume-nominal)>1e-6*nominal:raise ValueError('Meshed tetra volume differs from canonical stock')
    def add(rect,total):
        for n,f in surface_forces(model,rect,total).items():forces[n]+=f
    add([0.,20.,-1.,1.],spec['superimposed_mass_kg']*9.80665)
    # Actual selected full-axle force is split across two declared rail patches once.
    for p in spec['live_pose']['points']:
        x=p['x_m'];half=.15;a=max(0.,x-half);b=min(20.,x+half)
        if b-a<1e-8:raise ValueError('Axle patch outside span')
        for y in (-.6,.6):add([a,b,y-.1,y+.1],p['force_N']/2)
    depth=min(p[2] for p in nodes.values());supports=[]
    for lo,hi in ((0.,.3),(19.7,20.)):
        support=[int(n) for n,p in nodes.items() if lo-1e-8<=p[0]<=hi+1e-8 and abs(p[1])<=.25+1e-8 and abs(p[2]-depth)<1e-8]
        if len(support)<2:raise ValueError('Finite common bearing patch not resolved')
        supports.append(support)
    anchor=[min(s,key=lambda n:sum((nodes[str(n)][j]-target[j])**2 for j in range(3))) for s,target in zip(supports,([0.,0.,depth],[20.,0.,depth]))]
    probe=min(nodes,key=lambda n:sum((nodes[n][j]-[10.,0.,0.][j])**2 for j in range(3)))
    if max(abs(a-b) for a,b in zip(nodes[probe],[10.,0.,0.]))>1e-7:raise ValueError('Exact midspan deck observation node missing')
    applied=[0.,0.,fsum(forces.values())];moment=[fsum(nodes[str(n)][1]*f for n,f in forces.items()),-fsum(nodes[str(n)][0]*f for n,f in forces.items()),0.]
    model.update(nodal_load_N={str(n):[0.,0.,f] for n,f in forces.items()},support_nodes=supports,anchor_nodes=anchor,probe_nodes=[int(probe)],probe_xyz_m=[[10.,0.,0.]],
        applied_N=applied,applied_moment_Nm=moment,mesh_volume_m3=volume,nominal_selfweight_N=volume*2500.*9.80665,
        superimposed_weight_N=spec['superimposed_mass_kg']*9.80665,live_weight_N=fsum(p['force_N'] for p in spec['live_pose']['points']),
        stress_scope='One common exact midspan deck node; not global stress maximum or a concrete resistance criterion')
    expected=model['nominal_selfweight_N']+model['superimposed_weight_N']+model['live_weight_N']
    if abs(-applied[2]-expected)>1e-8*expected:raise ValueError('Force assembly does not close')
    return model


def commands(spec,model):
    cmd=lambda c,**p:dict(command=c,params=p)
    out=[cmd('model.units',system='m-kg-s-N-Pa')]
    out += [cmd('mesh.node.add',label=int(n),xyz=p) for n,p in model['nodes'].items()]
    out += [cmd('mesh.element.add',label=int(n),kind='tet10',nodes=e) for n,e in model['elements'].items()]
    out += [cmd('model.set.create',name='Body',elements=list(map(int,model['elements']))),
      cmd('model.material.create',name='ResearchConcrete',elastic=dict(type='isotropic',young=35e9,poisson=.2)),
      cmd('model.section.create',name='Continuum',set='Body',material='ResearchConcrete',kind=dict(type='solid'))]
    bc=[]
    for i,ns in enumerate(model['support_nodes']):
        name='Bearing'+str(i);out += [cmd('model.set.create',name=name,nodes=ns),
          cmd('model.boundary_condition.create',name=name,type='displacement',target=dict(set=name),values=[None,None,0.,None,None,None])];bc.append(name)
    for i,n in enumerate(model['anchor_nodes']):
        name='Anchor'+str(i);out += [cmd('model.set.create',name=name,nodes=[n]),
          cmd('model.boundary_condition.create',name=name,type='displacement',target=dict(set=name),values=[0. if i==0 else None,0.,None,None,None,None])];bc.append(name)
    for n,f in model['nodal_load_N'].items():
        out += [cmd('model.set.create',name='N'+n,nodes=[int(n)]),cmd('model.load.create',name='F'+n,type='force',target=dict(set='N'+n),vector=f,distribution='total')]
    out += [cmd('model.step.create',name='Research',procedure=dict(type='static'),boundary_conditions=bc,loads=['F'+n for n in model['nodal_load_N']]),
      cmd('model.check'),cmd('solve.static',step='Research'),cmd('solve.probe',step='Research',at=model['probe_xyz_m']),
      cmd('results.reactions',step='Research',sets=['Bearing0','Bearing1','Anchor0','Anchor1'],about=[0.,0.,0.]),cmd('model.info')]
    return out


def _residuals(force,moment,model):
    total=abs(model['applied_N'][2]);F=max(abs(a+b) for a,b in zip(force,model['applied_N']))/total
    M=max(abs(a+b) for a,b in zip(moment,model['applied_moment_Nm']))/(20*total)
    return dict(force_equilibrium_relative_residual=F,moment_equilibrium_relative_residual=M,
      force_equilibrium_passed=F<=SCREENS['force_relative'],moment_equilibrium_passed=M<=SCREENS['moment_relative'])


def parse_field(rows,model):
    check,solve,probe,reaction,info=rows[-5:]
    if check.get('errors')!=0 or not check.get('ready') or info.get('display_units')!='m-kg-s-N-Pa':raise ValueError('Native model or SI check failed')
    if info['nodes']!=len(model['nodes']) or info['elements']!={'tet10':len(model['elements'])}:raise ValueError('FieldCraft mesh differs')
    if reaction.get('stale') is not False or probe.get('units',{}).get('stress')!='Pa':raise ValueError('Current SI results required')
    p=probe['nodes'][0]
    if max(abs(a-b) for a,b in zip(p['xyz'],[10.,0.,0.]))>1e-7:raise ValueError('Common observation point differs')
    if any(not isfinite(x) for x in [*p['displacement'],p['von_mises']]):raise ValueError('Nonfinite readback')
    force=reaction['total']['force'];moment=reaction['total']['moment']
    return dict(displacement_m=p['displacement'],sampled_midspan_von_mises_Pa=p['von_mises'],stress_scope=model['stress_scope'],reaction_N=force,reaction_moment_Nm=moment,
      reaction_distribution=reaction['sets'],**_residuals(force,moment,model),**FLAGS)


def deck(spec,model):
    lines=['*HEADING','Canonical portfolio 20m exact-CAD continuum; SI; not selected beam reference','*NODE']
    lines += [n+','+','.join(f'{v:.12g}' for v in p) for n,p in model['nodes'].items()]
    lines+=['*ELEMENT,TYPE=C3D10,ELSET=BODY']
    lines += [','.join(map(str,[n,*ccx_nodes(e,model['nodes'])])) for n,e in model['elements'].items()]
    sets=[('BEARING0',model['support_nodes'][0]),('BEARING1',model['support_nodes'][1]),('ROOT',sorted(set(sum(model['support_nodes'],[])+model['anchor_nodes']))),('TIP',model['probe_nodes'])]
    for name,ns in sets:
        lines+=['*NSET,NSET='+name]+[','.join(map(str,ns[i:i+15])) for i in range(0,len(ns),15)]
    lines+=['*MATERIAL,NAME=CONCRETE','*ELASTIC','35000000000,.2','*SOLID SECTION,ELSET=BODY,MATERIAL=CONCRETE',
      '*BOUNDARY','BEARING0,3,3','BEARING1,3,3',f"{model['anchor_nodes'][0]},1,2",f"{model['anchor_nodes'][1]},2,2",'*STEP','*STATIC','*CLOAD']
    lines += [f'{n},3,{v[2]:.12g}' for n,v in model['nodal_load_N'].items()]
    return '\n'.join(lines+['*NODE PRINT,NSET=TIP','U','*NODE PRINT,NSET=ROOT','RF','*EL PRINT,ELSET=BODY','S','*END STEP',''])


def parse_ccx(text,model):
    u={};rf={};stress=[];mode=None
    for line in text.splitlines():
        low=line.lower()
        if 'displacements' in low:mode='u' if 'set tip' in low else None
        elif 'forces' in low:mode='rf' if 'set root' in low else None
        elif 'stresses' in low:mode='s'
        else:
            f=line.split()
            if mode in ('u','rf') and len(f)==4 and f[0].isdigit():(u if mode=='u' else rf)[int(f[0])]=[float(x.replace('D','E')) for x in f[1:]]
            elif mode=='s' and len(f)==8 and f[0].isdigit():
                xx,yy,zz,xy,xz,yz=map(float,f[2:]);stress.append(sqrt(((xx-yy)**2+(yy-zz)**2+(zz-xx)**2)/2+3*(xy*xy+xz*xz+yz*yz)))
    root=set(sum(model['support_nodes'],[])+model['anchor_nodes'])
    if set(u)!=set(model['probe_nodes']) or set(rf)!=root or not stress:raise ValueError('Independent solver readback coverage differs')
    force=[fsum(v[d] for v in rf.values()) for d in range(3)];moment=[0.,0.,0.]
    for n,v in rf.items():
        x,y,z=model['nodes'][str(n)];moment[0]+=y*v[2]-z*v[1];moment[1]+=z*v[0]-x*v[2];moment[2]+=x*v[1]-y*v[0]
    return dict(displacement_m=u[model['probe_nodes'][0]],reaction_N=force,reaction_moment_Nm=moment,
      integration_point_peak_von_mises_Pa=max(stress),stress_scope='Global integration-point maximum; includes restraint/load-patch concentrations, not the FieldCraft sampled nodal stress',
      reaction_distribution={str(n):v for n,v in rf.items()},**_residuals(force,moment,model),**FLAGS)


def solve(spec,model,output):
    folder=Path(output).resolve();folder.mkdir(parents=True,exist_ok=False);cmds=commands(spec,model)
    calls=[('batch',dict(commands=cmds[i:i+4000])) for i in range(0,len(cmds),4000)]
    execution,replies=native.mcp('fieldcraft',calls,folder/'fieldcraft',read_root=folder)
    result=dict(fieldcraft_execution=execution,calculix_executable_sha256=native.digest(shutil.which('ccx')))
    if execution['execution']=='executed':
        try:
            rows=[]
            for r in replies:
                if r.get('id',0)>1:rows.extend(batch_results(native.payload(r)))
            result['fieldcraft']=parse_field(rows,model)
        except (ValueError,KeyError,IndexError) as e:result['fieldcraft_failure']=str(e)[:2000]
    inp=folder/'viaduct.inp';inp.write_text(deck(spec,model))
    # The solve writes only its private native directory; input is an immutable read source.
    ccxfolder=folder/'calculix';argv=['/usr/bin/python3','-c',"import os,shutil;shutil.copyfile("+repr(str(inp))+",'viaduct.inp');os.execv('/usr/bin/ccx',['ccx','viaduct'])"]
    execution2=bounded(argv,ccxfolder,read_roots=(folder,))
    result['calculix_execution']=execution2
    if execution2['state']=='executed':
        try:
            dat=inp.with_suffix('.dat')
            if not dat.is_file():dat=ccxfolder/'viaduct.dat'
            result['calculix']=parse_ccx(dat.read_text(),model)
        except (ValueError,OSError,KeyError) as e:result['calculix_failure']=str(e)
    if all(k in result for k in ('fieldcraft','calculix')):
        a=result['fieldcraft']['displacement_m'][2];b=result['calculix']['displacement_m'][2]
        delta=abs(a-b)/max(abs(b),1e-30);result.update(cross_solver_displacement_relative_difference=delta,cross_solver_screen_passed=delta<=SCREENS['cross_solver_displacement_relative'])
    native.write(folder/'result.json',result);return result


def run(spec,output):
    folder=Path(output).resolve();folder.mkdir(parents=True,exist_ok=False)
    if spec['input_id']!=identity({k:v for k,v in spec.items() if k!='input_id'}):raise ValueError('Input seal differs')
    epoch=sources();native.write(folder/'input.json',spec);(folder/'evaluator-source.py').write_bytes(Path(__file__).read_bytes())
    request=dict(input_id=spec['input_id'],candidate_id=spec['candidate_id'],component_geometry_id=spec['component_geometry_id'],source_sha256=epoch,
      tools={n:native.pin(n) for n in ('solidcraft','fieldcraft')},runtime=platform.python_version(),screens=SCREENS,**FLAGS)
    request['evaluation_id']=identity(request);native.write(folder/'request.json',request);levels={}
    for level in ('coarse','fine'):
        try:
            m=mesh(spec,level,folder/('mesh-'+level));r=solve(spec,m,folder/('solve-'+level));levels[level]=dict(mesh_id=m['mesh_id'],node_count=len(m['nodes']),element_count=len(m['elements']),min_scaled_jacobian=m['min_scaled_jacobian'],results=r)
        except (ValueError,OSError,KeyError) as e:levels[level]=dict(state='held',reason=str(e))
    refinement=None
    if all('fieldcraft' in levels[l].get('results',{}) for l in ('coarse','fine')):
        a,b=[levels[l]['results']['fieldcraft']['displacement_m'][2] for l in ('coarse','fine')];d=abs(a-b)/abs(b)
        refinement=dict(displacement_relative_change=d,screen_passed=d<=SCREENS['displacement_refinement_relative'],mesh_independence_established=False)
    if epoch!=sources():raise ValueError('Evaluator source epoch changed; preserve run without promotion')
    result=dict(schema='osr-viaduct-fem/1',candidate_id=spec['candidate_id'],component_geometry_id=spec['component_geometry_id'],input_id=spec['input_id'],evaluation_id=request['evaluation_id'],levels=levels,refinement=refinement,
      unresolved=['Reinforcement/prestress, cracking, shear/strength, fatigue and approved material properties','Actual bearings, joints, foundations, rail fastening and support flexibility','Moving load envelope, torsion, dynamics, seismic, erection, lifting and accidental actions','Located complete installed mass and source-authenticated site loads'],**FLAGS)
    result['artifact_sha256']={p.relative_to(folder).as_posix():native.digest(p) for p in folder.rglob('*') if p.is_file()};result['result_id']=identity(result);native.write(folder/'result.json',result);return result


def verify(output,spec):
    """Read-only source/byte verification and raw numerical readback, no fresh solve."""
    folder=Path(output);r=json.loads((folder/'result.json').read_text());request=json.loads((folder/'request.json').read_text())
    if r['result_id']!=identity({k:v for k,v in r.items() if k!='result_id'}):raise ValueError('Result seal differs')
    if request['evaluation_id']!=identity({k:v for k,v in request.items() if k!='evaluation_id'}):raise ValueError('Request seal differs')
    if request['source_sha256']!=sources() or json.loads((folder/'input.json').read_text())!=spec:raise ValueError('Source or input differs')
    for k in ('candidate_id','component_geometry_id','input_id'):
        if r[k]!=spec[k] or request[k]!=spec[k]:raise ValueError('Mixed physical/evaluation identity')
    files={p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file() and p!=folder/'result.json'}
    if set(files)!=set(r['artifact_sha256']):raise ValueError('Artifact coverage differs')
    for n,p in files.items():
        if p.is_symlink() or native.digest(p)!=r['artifact_sha256'][n]:raise ValueError('Artifact changed '+n)
    if any(r.get(k) is not False for k in FLAGS):raise ValueError('Research results cannot confer physical acceptance')
    return dict(integrity_verified=True,fresh_native_solve=False,result_id=r['result_id'],scope='Source and immutable byte bindings, not authenticated physical evidence or an OS sandbox',**FLAGS)


TET_EDGES=((0,1),(1,2),(2,0),(0,3),(1,3),(2,3))

def ccx_nodes(element,nodes):
    corners=element[:4];remaining=list(element[4:]);ordered=list(corners)
    for a,b in TET_EDGES:
        point=[(nodes[str(corners[a])][j]+nodes[str(corners[b])][j])/2 for j in range(3)]
        matches=[n for n in remaining if max(abs(x-y) for x,y in zip(nodes[str(n)],point))<1e-7]
        if len(matches)!=1:raise ValueError('Independent CCX midside-edge map differs')
        ordered.append(matches[0]);remaining.remove(matches[0])
    return ordered

def validate_elements(model):
    import numpy as np
    for e in model['elements'].values():
        if len(e)!=10 or ccx_nodes(e,model['nodes'])!=e:raise ValueError('FieldCraft tetra10 midside order differs')
        p=np.array([model['nodes'][str(n)] for n in e[:4]])
        if float(np.linalg.det((p[1:]-p[0]).T))<=0:raise ValueError('Nonpositive signed tetrahedral Jacobian')
    return True
