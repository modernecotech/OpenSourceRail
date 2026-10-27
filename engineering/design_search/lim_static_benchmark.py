"""Independent GetDP static linear subset on the canonical moving-LIM mesh.

Prescribed closed-winding mathematical sources, linear mu_r=1000 steel, no
secondary eddy current, motion, circuit, controller, thermal or force admission.
Geometry is shared deliberately; GetDP assembles its own operator and source.
"""
from pathlib import Path
from time import monotonic
import argparse,json,os,shutil,signal,subprocess,sys,resource
import numpy as np
import scipy
import numpy._core._multiarray_umath as numpycore
import scipy.sparse.linalg._dsolve._superlu as superlu
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import identity,encoded,digest
from . import moving_lim as moving,transient_lim as transient,lim_materials

CODE='engineering/design_search/lim_static_benchmark.py'
MOTOR='be98f644c7c5117cb0423970c02501f234c3488689db8b0d017ef34dc6718dc5'
BUNDLE='70eb0ba82c796bc3ec3c52dbdb1c64db15b0d337c64a021f5a5ed3956a28fdc5'
REFERENCE='https://getdp.info/doc/texinfo/getdp.html#Magnetostatic-problem'
SCOPE='Same-mesh linear static prescribed-current field/operator subset only; no moving force, circuit, material, thermal, route, installed-equipment or operating-map qualification'
NAMES=('zero','quarter-current','reversed-current','unit-path')


def sources(root=ROOT):return {**moving.sources(root),CODE:digest(Path(root)/CODE),'engineering/station_rail/__init__.py':digest(Path(root)/'engineering/station_rail/__init__.py')}
def read(path):return json.loads(Path(path).read_bytes())
def write(path,value):Path(path).write_bytes(encoded(value))


def runtime():
    return dict(python=sys.version,python_executable_sha256=digest(sys.executable),numpy=np.__version__,numpy_core_sha256=digest(numpycore.__file__),scipy=scipy.__version__,superlu_sha256=digest(superlu.__file__),threads=1)


def tool(path=None):
    value=path or shutil.which('getdp')
    if not value:raise ValueError('Explicit --getdp executable or getdp on PATH required; no download/fallback')
    p=Path(value).resolve(strict=True)
    if not p.is_file():raise ValueError('Ordinary executable GetDP required')
    version=subprocess.run([str(p),'-version'],capture_output=True,text=True,timeout=10,check=True)
    if (version.stdout+version.stderr).strip()!='3.5.0':raise ValueError('This bounded benchmark requires GetDP3.5.0')
    info=subprocess.run([str(p),'-info'],capture_output=True,text=True,timeout=10,check=True)
    return dict(path=str(p),sha256=digest(p),version='3.5.0',version_stdout=version.stdout,version_stderr=version.stderr,build_info=info.stdout+info.stderr)


def case_requests(parent,currents):
    q=np.asarray(currents,dtype=float)
    if q.shape!=(30,) or not np.all(np.isfinite(q)) or max(abs(q))>140:raise ValueError('Explicit finite30-path current vector within numerical bound required')
    vectors=(np.zeros(30),q,-q,np.r_[1.,np.zeros(29)])
    context=dict(schema='osr-LIM-static-context/1',physical_bundle_id=parent['bundle_id'],body_candidate_id=parent['body_candidate_id'],motor_component_id=parent['motor_component_id'],physical_geometry=parent['physical_geometry'],wiring_hypothesis_id=parent['wiring_hypothesis_id'],parent_request_id=parent['request_id'],linear_steel_relative_mu=1000.,other_relative_mu=1.,secondary_eddy_current=False,motion=False,circuit=False,current_controller=False,source_interpretation='Imposed closed-winding mathematical sources; unit-path is not a permissible floating-neutral drive point',material_grade_verified=False,agreement_targets=dict(relative_A_B_energy=1e-6,operator_residual=1e-8,curl_B_absolute_T=1e-10),scope=SCOPE,**FLAGS)
    result=[]
    for name,values in zip(NAMES,vectors):
        r=dict(context=context,name=name,path_currents_A=values.tolist(),maximum_nodes=75000,memory_bytes=2*1024**3,internal_seconds=85.,external_seconds=90.,operating_map_admitted=False,**FLAGS)
        r['request_id']=identity(r);result.append(r)
    return result


def mesh_data(parent):
    points,tri,regions,boundary,branch,sign=moving.mesh(parent)
    area,grad=transient.geometry(points,tri)
    # Derive export source groups independently from physical slot positions,
    # side, period and declared phase register, rather than copying W entries.
    p=parent['physical_geometry'];centers=points[tri].mean(axis=1);pitch=2*p['pole_pitch_m']/6
    half=p['secondary_thickness_m']/2;face=half+p['gap_each_side_m'];back=face+p['slot_depth_m']
    slot=np.floor(centers[:,0]/pitch).astype(int);valid=(slot>=0)&(slot<6*p['periods'])
    offset=centers[:,0]-(slot+.5)*pitch
    coil=valid&(abs(offset)<p['slot_width_m']/2)&(abs(centers[:,1])>face)&(abs(centers[:,1])<back)
    phase=np.asarray([0,2,1,0,2,1])[slot[coil]%6];polarity=np.asarray([1,-1,1,-1,1,-1])[slot[coil]%6]
    coil_index=np.where(centers[coil,1]<0,0,25)+slot[coil]//6
    derived=phase*10+coil_index%10
    if not np.array_equal(coil,branch>=0) or not np.array_equal(derived,branch[coil]) or not np.array_equal(polarity,sign[coil]):raise ValueError('Semantic winding register differs from canonical mesh')
    tags=np.where(regions==3,3,1);tags[coil]=1000+2*derived+(polarity<0)
    for k in range(30):
        for s in (0,1):
            if not np.isclose(sum(area[tags==1000+2*k+s]),5*p['slot_width_m']*p['slot_depth_m'],rtol=1e-10,atol=1e-12):raise ValueError('Five signed slot legs per path not preserved')
    # Independently recover exterior line entities from triangle incidence.
    edges=np.sort(np.concatenate((tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]])),axis=1)
    unique,count=np.unique(edges,axis=0,return_counts=True);outer=unique[count==1]
    if not np.array_equal(np.unique(outer),boundary):raise ValueError('Exterior edge/node boundary differs')
    return points,tri,regions,boundary,branch,sign,area,grad,tags,outer


def msh_text(points,tri,tags,outer):
    rows=['$MeshFormat','2.2 0 8','$EndMeshFormat','$Nodes',str(len(points))]
    rows.extend(f'{k+1} {x:.17g} {y:.17g} 0' for k,(x,y) in enumerate(points));rows.extend(('$EndNodes','$Elements',str(len(tri)+len(outer))))
    rows.extend(f'{k+1} 2 2 {int(tag)} {int(tag)} '+ ' '.join(str(int(n)+1) for n in cell) for k,(cell,tag) in enumerate(zip(tri,tags)))
    rows.extend(f'{len(tri)+k+1} 1 2 901 901 {int(a)+1} {int(b)+1}' for k,(a,b) in enumerate(outer));rows.append('$EndElements');return '\n'.join(rows)+'\n'


def formulation(parent,currents):
    p=parent['physical_geometry'];groups=','.join(map(str,range(1000,1060)));density=p['turns_per_coil']/(p['slot_width_m']*p['slot_depth_m'])
    js='\n'.join(f'js[Region[{1000+2*k+s}]]=Vector[0,0,{((-1)**s*density*i):.17g}];' for k,i in enumerate(currents) for s in (0,1))
    return f'''// Independent static A_z weak form from official GetDP magnetostatics template.
mu0=4.e-7*Pi;
Group{{Air=Region[1];Steel=Region[3];Coils=Region[{{{groups}}}];Domain=Region[{{Air,Steel,Coils}}];Outer=Region[901];}}
Function{{nu[Region[{{Air,Coils}}]]=1/mu0;nu[Steel]=1/(1000*mu0);{js}}}
Constraint{{{{Name Boundary;Case{{{{Region Outer;Value 0.;}}}}}}}}
Jacobian{{{{Name Vol;Case{{{{Region All;Jacobian Vol;}}}}}}}}
Integration{{{{Name Gauss;Case{{{{Type Gauss;Case{{{{GeoElement Triangle;NumberOfPoints 3;}}}}}}}}}}}}
FunctionSpace{{{{Name As;Type Form1P;BasisFunction{{{{Name sn;NameOfCoef an;Function BF_PerpendicularEdge;Support Domain;Entity NodesOf[All];}}}}Constraint{{{{NameOfCoef an;EntityType NodesOf;NameOfConstraint Boundary;}}}}}}}}
Formulation{{{{Name Static;Type FemEquation;Quantity{{{{Name a;Type Local;NameOfSpace As;}}}}Equation{{
Integral{{[nu[]*Dof{{d a}},{{d a}}];In Domain;Jacobian Vol;Integration Gauss;}}
Integral{{[-js[],{{a}}];In Coils;Jacobian Vol;Integration Gauss;}}
}}}}}}
Resolution{{{{Name Solve;System{{{{Name S;NameOfFormulation Static;}}}}Operation{{Generate[S];Solve[S];SaveSolution[S];}}}}}}
PostProcessing{{{{Name Result;NameOfFormulation Static;Quantity{{
{{Name az;Value{{Local{{[CompZ[{{a}}]];In Domain;Jacobian Vol;}}}}}}
{{Name b;Value{{Term{{[{{d a}}];In Domain;Jacobian Vol;}}}}}}
{{Name energy;Value{{Integral{{[.5*nu[]*SquNorm[{{d a}}]];In Domain;Jacobian Vol;Integration Gauss;}}}}}}
{{Name work;Value{{Integral{{[CompZ[js[]]*CompZ[{{a}}]];In Coils;Jacobian Vol;Integration Gauss;}}}}}}
}}}}}}
PostOperation{{{{Name Result;NameOfPostProcessing Result;Operation{{
Print[az,OnElementsOf Domain,File "a.txt",Format NodeTable];
Print[b,OnElementsOf Domain,Depth 0,File "b.txt",Format ElementTable];
Print[energy[Domain],OnGlobal,File "energy.txt",Format Table];
Print[work[Coils],OnGlobal,File "work.txt",Format Table];
}}}}}}
'''


def reference(parent,currents,data,*,solve=True,A=None):
    points,tri,regions,boundary,branch,sign,area,grad,tags,outer=data;p=parent['physical_geometry'];N=len(points)
    _,local,*_=transient.magnetic(np.zeros(N),tri,area,grad,regions,lim_materials.material(),True)
    rr=np.repeat(tri,3,axis=1).ravel();cc=np.tile(tri,(1,3)).ravel();K=coo_matrix((local.ravel(),(rr,cc)),shape=(N,N)).tocsr()
    J=np.zeros(len(tri));coil=branch>=0;J[coil]=p['turns_per_coil']*sign[coil]*np.asarray(currents)[branch[coil]]/(p['slot_width_m']*p['slot_depth_m'])
    f=np.bincount(tri.ravel(),weights=np.repeat(area*J/3,3),minlength=N);free=np.setdiff1d(np.arange(N),boundary)
    if solve:
        A=np.zeros(N)
        if np.any(f):A[free]=spsolve(K[free][:,free],f[free])
    A=np.asarray(A);ga=np.einsum('ti,tij->tj',A[tri],grad);B=np.stack((ga[:,1],-ga[:,0],np.zeros(len(tri))),axis=1)
    nu=np.where(regions==3,1/(transient.MU0*1000),1/transient.MU0);energy=float(np.sum(.5*area*nu*np.sum(B*B,axis=1)));work=float(area@(J*A[tri].mean(axis=1)))
    residual=float(np.linalg.norm((K@A-f)[free])/max(np.linalg.norm(f[free]),1e-30))
    return dict(A=A,B=B,nu=nu,J=J,energy_per_m_J_m=energy,source_work_per_m_J_m=work,relative_operator_residual=residual)


def node_table(path,N):
    lines=[line.split() for line in Path(path).read_text().splitlines() if line.strip() and not line.startswith('#')]
    if len(lines[0])==1:lines=lines[1:]
    a=np.full(N,np.nan)
    for row in lines:
        if len(row)!=2:raise ValueError('Scalar NodeTable shape differs')
        k=int(row[0])-1
        if not 0<=k<N or np.isfinite(a[k]):raise ValueError('Duplicate/outside NodeTable node')
        a[k]=float(row[1])
    if not np.all(np.isfinite(a)):raise ValueError('Incomplete/nonfinite NodeTable')
    return a


def element_table(path,E):
    lines=[line.split() for line in Path(path).read_text().splitlines() if line.strip() and not line.startswith('#')]
    if len(lines[0])==1:lines=lines[1:]
    b=np.full((E,3),np.nan)
    for row in lines:
        k=int(row[0])-1;v=np.asarray(list(map(float,row[1:])))
        if not 0<=k<E or len(v) not in (3,9) or np.any(np.isfinite(b[k])):raise ValueError('ElementTable index/vector shape differs')
        v=v.reshape(-1,3)
        if not np.allclose(v,v[0],rtol=1e-12,atol=1e-14):raise ValueError('P1 cell curl is not constant')
        b[k]=v[0]
    if not np.all(np.isfinite(b)):raise ValueError('Incomplete/nonfinite ElementTable')
    return b


def scalar(path):
    rows=[line.split() for line in Path(path).read_text().splitlines() if line.strip() and not line.startswith('#')]
    return float(rows[-1][1])


def analyze(folder,parent,currents,data):
    folder=Path(folder);points,tri,regions,boundary,branch,sign,area,grad,tags,outer=data
    with np.load(folder/'reference.npz') as value:ref=reference(parent,currents,data,solve=False,A=value['A'])
    A=node_table(folder/'a.txt',len(points));B=element_table(folder/'b.txt',len(tri));check=reference(parent,currents,data,solve=False,A=A)
    energy=scalar(folder/'energy.txt');work=scalar(folder/'work.txt');height=parent['physical_geometry']['active_height_m']
    bnorm=np.sqrt(np.sum(area[:,None]*ref['B']**2));bdiff=np.sqrt(np.sum(area[:,None]*(B-ref['B'])**2));anorm=np.linalg.norm(ref['A']);adiff=np.linalg.norm(A-ref['A'])
    result=dict(nodal_A_relative_L2=float(adiff/max(anorm,1e-30)),nodal_A_maximum_absolute_Wb_m=float(max(abs(A-ref['A']))),cell_B_relative_area_L2=float(bdiff/max(bnorm,1e-30)),cell_B_maximum_absolute_T=float(max(abs(B-ref['B']).ravel())),getdp_B_vs_curl_A_maximum_absolute_T=float(max(abs(B-check['B']).ravel())),boundary_A_maximum_absolute_Wb_m=float(max(abs(A[boundary]))),reference_operator_residual=ref['relative_operator_residual'],getdp_operator_residual=check['relative_operator_residual'],reference_energy_per_m_J_m=ref['energy_per_m_J_m'],getdp_energy_per_m_J_m=energy,reference_energy_J=height*ref['energy_per_m_J_m'],getdp_energy_J=height*energy,getdp_source_work_J=height*work,energy_relative_error=abs(energy-ref['energy_per_m_J_m'])/max(abs(ref['energy_per_m_J_m']),1e-30),getdp_source_work_minus_twice_energy_J=height*(work-2*energy),reference_source_work_minus_twice_energy_J=height*(ref['source_work_per_m_J_m']-2*ref['energy_per_m_J_m']),getdp_energy_vs_B_integral_relative_error=abs(energy-check['energy_per_m_J_m'])/max(abs(energy),1e-30),global_imposed_source_current_A=float(area@ref['J']),maximum_imposed_Jz_A_m2=float(max(abs(ref['J']))))
    # Declared numerical agreement targets are software checks, not physical limits.
    result['numerical_subset_agreement']=all(result[k]<=1e-6 for k in ('nodal_A_relative_L2','cell_B_relative_area_L2','energy_relative_error','getdp_energy_vs_B_integral_relative_error')) and result['getdp_operator_residual']<=1e-8 and result['getdp_B_vs_curl_A_maximum_absolute_T']<=1e-10
    return result


def prepare(output,parent_folder,getdp=None,root=ROOT):
    root=Path(root);output=Path(output)
    if output.exists():raise ValueError('Fresh private benchmark directory required')
    parent_folder=Path(parent_folder);moving.verify(parent_folder,root=root);inp=read(parent_folder/'input.json');result=read(parent_folder/'result.json');parent=inp['request']
    if parent['motor_component_id']!=MOTOR or parent['bundle_id']!=BUNDLE or parent['mesh_definition']['critical_dx_m']!=.005 or parent['mesh_definition']['secondary_dy_m']!=.0009375 or result['trace'][-1]['time_s']!=.016:raise ValueError('Exact canonical fine-mesh parent/final state required')
    data=mesh_data(parent);mesh=moving.mesh_fingerprint(*data[:6])
    if mesh!=result['actual_mesh'] or len(data[0])>75000:raise ValueError('Actual parent mesh differs or exceeds bound')
    cases=case_requests(parent,result['trace'][-1]['path_currents_A']);native=tool(getdp);epoch=sources(root)
    plan=dict(schema='osr-LIM-static-plan/1',parent_request=parent,parent_evaluation_id=result['evaluation_id'],parent_result_sha256=digest(parent_folder/'result.json'),cases=cases,source_sha256=epoch,tool=native,runtime=runtime(),actual_mesh=mesh,nodes=len(data[0]),elements=len(data[1]),free_nodes=len(data[0])-len(data[3]),signed_source_regions=60,COO_entry_upper_bound=9*len(data[1]),COO_storage_bytes_upper_bound=24*9*len(data[1]),factorization_peak_RAM_bytes=None,runtime_guaranteed=False,maximum_component_jobs=4,maximum_campaign_seconds=240,maximum_nodes=75000,source_git_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),scope=SCOPE,physical_accepted=False,operating_map_admitted=False)
    plan['plan_id']=identity(plan);output.mkdir(parents=True)
    for name in epoch:
        dest=output/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,dest)
    shutil.copytree(parent_folder,output/'parent');write(output/'plan.json',plan);return plan


def _worker(folder):
    folder=Path(folder);request=read(folder/'input.json');plan=request['plan'];case=request['case'];started=monotonic();data=mesh_data(plan['parent_request'])
    if sources()!=plan['source_sha256'] or digest(plan['tool']['path'])!=plan['tool']['sha256'] or runtime()!=plan['runtime']:raise ValueError('Frozen source/tool/runtime differs')
    (folder/'model.msh').write_text(msh_text(data[0],data[1],data[8],data[9]));(folder/'model.pro').write_text(formulation(plan['parent_request'],case['path_currents_A']))
    ref=reference(plan['parent_request'],case['path_currents_A'],data);np.savez(folder/'reference.npz',A=ref['A'],B=ref['B'])
    command=[plan['tool']['path'],'model.pro','-msh','model.msh','-solve','Solve','-pos','Result','-v','4','-skip_petscrc','-ksp_type','cg','-pc_type','icc','-ksp_rtol','1e-12','-ksp_atol','1e-14','-ksp_max_it','20000','-ksp_error_if_not_converged']
    write(folder/'command.json',dict(command=command,threads=1));remaining=85-(monotonic()-started)
    if remaining<=0:raise TimeoutError('Reference preparation exhausted85s job budget')
    environment={k:v for k,v in os.environ.items() if k!='PETSC_OPTIONS'}
    try:p=subprocess.run(command,cwd=folder,capture_output=True,timeout=remaining,env={**environment,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
    except subprocess.TimeoutExpired as error:
        (folder/'stdout.log').write_bytes(error.stdout or b'');(folder/'stderr.log').write_bytes(error.stderr or b'');raise TimeoutError('Internal85s budget exhausted; native output retained')
    (folder/'stdout.log').write_bytes(p.stdout);(folder/'stderr.log').write_bytes(p.stderr)
    if p.returncode:raise RuntimeError('GetDP returned'+str(p.returncode))
    return dict(execution='completed',analysis=analyze(folder,plan['parent_request'],case['path_currents_A'],data),elapsed_s=monotonic()-started)


def run(output,root=ROOT):
    root=Path(root);output=Path(output);plan=read(output/'plan.json')
    if plan['plan_id']!=identity({k:v for k,v in plan.items() if k!='plan_id'}) or sources(root)!=plan['source_sha256']:raise ValueError('Frozen plan/source differs')
    currents=read(output/'parent'/'result.json')['trace'][-1]['path_currents_A']
    if plan['cases']!=case_requests(plan['parent_request'],currents):raise ValueError('Case source/context differs')
    started=monotonic();rows=[];preflight_hold=None
    for case in plan['cases']:
        folder=output/case['name']
        if folder.exists():raise ValueError('No retries/overwriting case packages')
        if preflight_hold is not None:
            rows.append(dict(name=case['name'],execution='pending-zero-preflight',reason=preflight_hold,request_id=case['request_id'],physical_accepted=False));continue
        if monotonic()-started+90>240:
            rows.append(dict(name=case['name'],execution='pending-total-budget',request_id=case['request_id'],physical_accepted=False));continue
        folder.mkdir();write(folder/'input.json',dict(plan=plan,case=case));t=monotonic()
        def limit():resource.setrlimit(resource.RLIMIT_AS,(case['memory_bytes'],case['memory_bytes']))
        proc=subprocess.Popen([sys.executable,'-m','engineering.design_search.lim_static_benchmark','worker','--output',str(folder)],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,preexec_fn=limit,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        try:stdout,stderr=proc.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGKILL);stdout,stderr=proc.communicate(timeout=5)
        (folder/'worker-stdout.log').write_bytes(stdout);(folder/'worker-stderr.log').write_bytes(stderr)
        result=read(folder/'worker-result.json') if (folder/'worker-result.json').exists() else dict(execution='interrupted',reason='Worker missing after external90s/error; raw files retained')
        if sources(root)!=plan['source_sha256'] or digest(plan['tool']['path'])!=plan['tool']['sha256']:raise ValueError('Source/tool changed; unsealed partial packages retained')
        result.update(name=case['name'],request_id=case['request_id'],plan_id=plan['plan_id'],elapsed_outer_s=monotonic()-t,physical_accepted=False,operating_map_admitted=False,scope=SCOPE);result['evaluation_id']=identity(result);write(folder/'result.json',result);rows.append(result)
        if case['name']=='zero' and (result['execution']!='completed' or not result['analysis']['numerical_subset_agreement']):preflight_hold='Zero-source tool/operator control failed; resolve definition before further native attempts'
        print(json.dumps({k:v for k,v in result.items() if k!='analysis'}),flush=True)
    report=dict(schema='osr-LIM-static-campaign/1',plan_id=plan['plan_id'],source_sha256=plan['source_sha256'],rows=rows,attempted_jobs=sum(not r['execution'].startswith('pending-') for r in rows),completed_jobs=sum(r['execution']=='completed' for r in rows),elapsed_s=monotonic()-started,scope=SCOPE,physical_accepted=False,operating_map_admitted=False)
    report['campaign_id']=identity(report);write(output/'campaign.json',report)
    inventory={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    manifest=dict(plan_id=plan['plan_id'],campaign_id=report['campaign_id'],files_sha256=inventory,physical_accepted=False);manifest['manifest_id']=identity(manifest);write(output/'manifest.json',manifest);return report


def verify(output,root=ROOT):
    output=Path(output);plan=read(output/'plan.json');manifest=read(output/'manifest.json');report=read(output/'campaign.json')
    if manifest['manifest_id']!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('Static manifest identity differs')
    inventory={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.relative_to(output).as_posix()!='manifest.json'}
    if inventory!=manifest['files_sha256'] or sources(root)!=plan['source_sha256'] or digest(plan['tool']['path'])!=plan['tool']['sha256']:raise ValueError('Static payload/source/tool differs')
    if plan['plan_id']!=identity({k:v for k,v in plan.items() if k!='plan_id'}) or report['campaign_id']!=identity({k:v for k,v in report.items() if k!='campaign_id'}):raise ValueError('Static plan/campaign identity differs')
    if report['physical_accepted'] is not False or report['operating_map_admitted'] is not False:raise ValueError('Static subset cannot grant acceptance')
    if len(report['rows'])!=len(plan['cases']) or plan['cases']!=case_requests(plan['parent_request'],read(output/'parent'/'result.json')['trace'][-1]['path_currents_A']):raise ValueError('Static case inventory/source differs')
    data=mesh_data(plan['parent_request'])
    for case,row in zip(plan['cases'],report['rows']):
        if row['name']!=case['name'] or row.get('request_id')!=case['request_id'] or row.get('physical_accepted') is not False:raise ValueError('Static row identity/disposition differs')
        if not row['execution'].startswith('pending-') and row!=read(output/case['name']/'result.json'):raise ValueError('Static case/campaign row differs')
        if row['execution']=='completed' and row['analysis']!=analyze(output/case['name'],plan['parent_request'],case['path_currents_A'],data):raise ValueError('Static derived analysis differs')
    return dict(verified=True,campaign_id=report['campaign_id'],physical_accepted=False,operating_map_admitted=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('plan','run','verify','worker'));parser.add_argument('--output',type=Path,required=True);parser.add_argument('--parent',type=Path);parser.add_argument('--getdp');args=parser.parse_args()
    if args.action=='worker':
        try:result=_worker(args.output)
        except Exception as error:result=dict(execution='interrupted' if isinstance(error,TimeoutError) else 'held',reason=type(error).__name__+': '+str(error))
        write(args.output/'worker-result.json',result);return
    result=prepare(args.output,args.parent,args.getdp) if args.action=='plan' else run(args.output) if args.action=='run' else verify(args.output)
    print(json.dumps(result if args.action=='verify' else {k:v for k,v in result.items() if k not in ('rows','cases','parent_request')},indent=2))


if __name__=='__main__':main()
