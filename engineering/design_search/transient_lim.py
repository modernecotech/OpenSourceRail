"""Research P1 A_z/u transient LIM, with a FIXED finite conductor mask.

The velocity term is an Eulerian frozen-position approximation. This is neither
moving geometry nor a supplied-steel/3D/thermal/available-force-map capability.
Backward Euler work includes positive algorithmic magnetic dissipation; hiding
that term would manufacture a false continuous energy balance.
"""
from pathlib import Path
from copy import deepcopy
from math import pi,isfinite,sqrt
from time import monotonic
import json,os,sys,subprocess,resource
import scipy
import numpy as np
from scipy.sparse import coo_matrix,bmat,csr_matrix
from scipy.sparse.linalg import spsolve
from engineering.station_rail import ROOT,FLAGS,long_motor,station_motor
from engineering.station_rail.common import identity,digest,encoded,source_map
from . import lim_materials
PRODUCER='engineering/design_search/transient_lim.py'
PRODUCERS=(PRODUCER,long_motor.PRODUCER,station_motor.PRODUCER,'engineering/station_rail/common.py','engineering/station_rail/__init__.py','engineering/design_search/lim_materials.py',lim_materials.DATA)
MU0=4e-7*pi
SCOPE='Fixed finite2D conductor mask, prescribed frozen velocity and phase currents; global return-current closure; no physical transit, 3D return path, inverter, supplier steel or available operating map'


def case(*,current_peak_A=25.,speed_m_s=10.,frequency_Hz=30.,phase_direction=1,steps_per_period=32,periods=3,linear=False):
    if not all(type(v) in (int,float) and isfinite(v) for v in (current_peak_A,speed_m_s,frequency_Hz)) or not 0<=current_peak_A<=140 or abs(speed_m_s)>10 or not 1<=frequency_Hz<=100 or phase_direction not in (-1,1):raise ValueError('Bounded finite current/frequency and frozen velocity required')
    if type(linear) is not bool:raise ValueError('Explicit boolean method control required')
    if type(steps_per_period) is not int or not 16<=steps_per_period<=64 or type(periods) is not int or not 1<=periods<=6:raise ValueError('Bounded transient16..64steps/period,1..6periods required')
    c=station_motor.case(frequency_Hz=frequency_Hz,current_peak_A=current_peak_A,mesh_m=.02);c.pop('case_id')
    c.update(periods=1,active_length_m=.5,secondary_length_m=.3,secondary_start_x_m=.1,secondary_end_x_m=.4,
        plate_gap_mesh_m=.00375,transverse_outer_air_margin_m=.2,outer_margin_m=.5,speed_m_s=speed_m_s,
        phase_direction=phase_direction,aluminium_conductivity_S_m=20e6,steps_per_period=steps_per_period,time_periods=periods,
        dt_s=1/frequency_Hz/steps_per_period,linear_reference=linear,maximum_nodes=16000,maximum_steps=384,
        scope=SCOPE,position_changes_during_solve=False)
    c['case_id']=identity(c);return c


def definition(c):
    source=station_motor.definition()
    keys=('wavelength_m','slot_pitch_m','slot_width_m','slot_depth_m','backiron_m','active_height_m','secondary_thickness_m','turns_per_coil','conductor_area_m2')
    d={key:source[key] for key in keys}
    geometry=dict(d,primary_length_m=c['active_length_m'],secondary_length_m=c['secondary_length_m'],secondary_start_x_m=c['secondary_start_x_m'],secondary_end_x_m=c['secondary_end_x_m'],gap_each_side_m=c['gap_each_side_m'],primary_sides=2,periods=c['periods'])
    d.update(secondary_length_m=c['secondary_length_m'],motor_component_id=identity(geometry),fixture_geometry=geometry,source_motor_definition_id=source['motor_component_id'])
    return d


def validate_case(c):
    expected=case(current_peak_A=c['current_peak_A'],speed_m_s=c['speed_m_s'],frequency_Hz=c['frequency_Hz'],phase_direction=c['phase_direction'],steps_per_period=c['steps_per_period'],periods=c['time_periods'],linear=c['linear_reference'])
    if c!=expected:raise ValueError('Transient geometry/resource/context differs from bounded constructor')


def formulation_description():
    return dict(potential='A_z',flux_density='B=(dA/dy,-dA/dx)',electric_drive='D=dA/dt+u+v*dA/dx',secondary_current='J_z=-sigma*D',weak_form='Integral(nu*gradA.gradw+sigma*D*w-Js(t)*w)=0',floating_closure='Integral_plate(sigma*D)=0',time_scheme='Backward Euler',material='piecewise-linear inverse H(B), exact stored energy and consistent differential tangent',scope=SCOPE)


def constitutive(B,curve,linear=False):
    """H(B), differential reluctivity and stored energy, with no extrapolation."""
    B=np.asarray(B,dtype=float)
    if np.any(~np.isfinite(B)) or np.any(B<0):raise ValueError('Nonnegative finite flux magnitude required')
    if linear:return B/(MU0*1000),np.full(B.shape,1/(MU0*1000)),B*B/(2*MU0*1000)
    lim_materials.validate(curve);b=np.asarray(curve['B_T']);h=np.asarray(curve['H_A_m'])
    if np.any(B>b[-1]):raise ValueError('Generic material table domain exceeded; extrapolation refused')
    i=np.clip(np.searchsorted(b,B,side='right')-1,0,len(b)-2);slopes=np.diff(h)/np.diff(b)
    cumulative=np.r_[0,np.cumsum((h[:-1]+h[1:])*np.diff(b)/2)];delta=B-b[i]
    return h[i]+slopes[i]*delta,slopes[i],cumulative[i]+h[i]*delta+.5*slopes[i]*delta*delta


def phase_current_density(region,time,c,d):
    if region not in range(100,106):return 0.
    return d['turns_per_coil']*c['current_peak_A']/(d['slot_width_m']*d['slot_depth_m'])*np.cos(2*pi*c['frequency_Hz']*time-c['phase_direction']*(region-100)*pi/3)


def read_mesh(path):
    lines=Path(path).read_text().splitlines();nodes={};tri=[];regions=[];boundary=set();i=0
    while i<len(lines):
        if lines[i]=='$Nodes':
            n=int(lines[i+1])
            for line in lines[i+2:i+2+n]:f=line.split();nodes[int(f[0])]=list(map(float,f[1:3]))
            i+=n+2
        elif lines[i]=='$Elements':
            n=int(lines[i+1])
            for line in lines[i+2:i+2+n]:
                f=list(map(int,line.split()));kind=f[1];nt=f[2];tag=f[3];ids=f[3+nt:]
                if kind==2:tri.append(ids);regions.append(tag)
                elif kind==1 and tag==901:boundary.update(ids)
            i+=n+2
        else:i+=1
    keys=sorted(nodes);index={k:i for i,k in enumerate(keys)}
    if any(len(t)!=3 for t in tri) or any(len(p)!=2 or not all(isfinite(x) for x in p) for p in nodes.values()):raise ValueError('Finite linear 2D triangle mesh required')
    if not tri or not boundary or not {2,3}<=set(regions):raise ValueError('Explicit P1 triangles/secondary/steel/outer boundary required')
    return np.array([nodes[k] for k in keys]),np.array([[index[n] for n in t] for t in tri]),np.array(regions),np.array(sorted(index[n] for n in boundary))


def geometry(points,triangles):
    p=points[triangles];twice=(p[:,1,0]-p[:,0,0])*(p[:,2,1]-p[:,0,1])-(p[:,2,0]-p[:,0,0])*(p[:,1,1]-p[:,0,1])
    if np.any(abs(twice)<1e-18):raise ValueError('Degenerate triangle')
    gradients=np.stack([np.stack([p[:,1,1]-p[:,2,1],p[:,2,0]-p[:,1,0]],axis=1),np.stack([p[:,2,1]-p[:,0,1],p[:,0,0]-p[:,2,0]],axis=1),np.stack([p[:,0,1]-p[:,1,1],p[:,1,0]-p[:,0,0]],axis=1)],axis=1)/twice[:,None,None]
    return abs(twice)/2,gradients


def magnetic(a,tri,area,grad,regions,curve,linear=False):
    ga=np.einsum('ti,tij->tj',a[tri],grad);B=np.linalg.norm(ga,axis=1);nu=np.full(len(tri),1/MU0);dnu=nu.copy();W=B*B/(2*MU0)
    steel=regions==3;H,tangent,energy=constitutive(B[steel],curve,linear)
    initial=curve['H_A_m'][1]/curve['B_T'][1] if not linear else 1/(MU0*1000)
    nu[steel]=np.divide(H,B[steel],out=np.full(H.shape,initial),where=B[steel]>1e-14);dnu[steel]=tangent;W[steel]=energy
    gg=np.einsum('tik,tjk->tij',grad,grad);dots=np.einsum('tik,tk->ti',grad,ga)
    local=area[:,None,None]*nu[:,None,None]*gg
    extra=np.divide(dnu-nu,B*B,out=np.zeros(B.shape),where=B>1e-14)
    jac=local+area[:,None,None]*extra[:,None,None]*dots[:,:,None]*dots[:,None,:]
    residual=np.einsum('tij,tj->ti',local,a[tri])
    return residual,jac,ga,B,nu,W


def solve(points,tri,regions,boundary,c,d,curve,*,deadline=None,progress=None):
    area,grad=geometry(points,tri);N=len(points);free=np.array(sorted(set(range(N))-set(boundary)));plate=regions==2;sigma=c['aluminium_conductivity_S_m'];speed=c['speed_m_s'];dt=c['dt_s']
    lengths=np.max(np.linalg.norm(points[tri][:,:,None,:]-points[tri][:,None,:,:],axis=-1),axis=(1,2));Pe=float(np.max(abs(speed)*lengths[plate]*MU0*sigma/2))
    if Pe>1:raise ValueError('Unstabilized P1 conductor Peclet>1; refine or independently validate stabilization')
    rr=np.repeat(tri,3,axis=1).ravel();cc=np.tile(tri,(1,3)).ravel()
    def matrix(values):return coo_matrix((values.ravel(),(rr,cc)),shape=(N,N)).tocsr()
    mass=matrix((sigma*area*plate/12)[:,None,None]*(np.eye(3)+np.ones((3,3)))[None,:,:])
    convection=matrix((sigma*area*plate*speed/3)[:,None,None]*np.broadcast_to(grad[:,:,0][:,None,:],(len(tri),3,3)))
    floating=np.bincount(tri.ravel(),weights=np.repeat(sigma*area*plate/3,3),minlength=N);closure=np.asarray(convection.sum(axis=0)).ravel();volume_sigma=float(sum(sigma*area[plate]))
    A=np.zeros(N);u=0.;rows=[];height=d['active_height_m'];initialW=0.;lastW=0.
    for step in range(1,c['steps_per_period']*c['time_periods']+1):
        if deadline and monotonic()>deadline:raise TimeoutError('Bounded transient time budget')
        old=A.copy();time=step*dt;Js=np.array([phase_current_density(int(tag),time,c,d) for tag in regions]);f=np.bincount(tri.ravel(),weights=np.repeat(area*Js/3,3),minlength=N);scale=max(np.linalg.norm(f),1.)
        for iteration in range(32):
            if deadline and monotonic()>deadline:raise TimeoutError('Bounded nonlinear iteration time budget')
            local,jac,ga,B,nu,W=magnetic(A,tri,area,grad,regions,curve,c['linear_reference']);res=np.bincount(tri.ravel(),weights=local.ravel(),minlength=N)+mass@((A-old)/dt)+convection@A+floating*u-f
            net=float(floating@((A-old)/dt)+closure@A+volume_sigma*u);R=np.r_[res[free],net]
            if np.linalg.norm(R)/scale<1e-8:break
            K=matrix(jac)+mass/dt+convection;J=bmat([[K[free][:,free],csr_matrix(floating[free,None])],[csr_matrix((floating[free]/dt+closure[free])[None,:]),csr_matrix([[volume_sigma]])]],format='csc')
            correction=spsolve(J,-R)
            if np.any(~np.isfinite(correction)):raise ValueError('Nonfinite nonlinear update')
            accepted=False
            for damping in (1.,.5,.25,.125,.0625):
                trial=A.copy();trial[free]+=damping*correction[:-1]
                try:triallocal,*_=magnetic(trial,tri,area,grad,regions,curve,c['linear_reference'])
                except ValueError:continue
                trialu=u+damping*correction[-1]
                trialres=np.bincount(tri.ravel(),weights=triallocal.ravel(),minlength=N)+mass@((trial-old)/dt)+convection@trial+floating*trialu-f
                trialnet=float(floating@((trial-old)/dt)+closure@trial+volume_sigma*trialu)
                if np.linalg.norm(np.r_[trialres[free],trialnet]) >= np.linalg.norm(R):continue
                A=trial;u=trialu;accepted=True;break
            if not accepted:raise ValueError('No domain-valid residual-reducing Newton update')
        else:raise ValueError('Nonlinear residual did not converge')
        At=(A-old)/dt;delta_grad=np.einsum('ti,tij->tj',(A-old)[tri],grad)/dt
        D=At[tri]+u+speed*ga[:,0,None];meanD=D.mean(axis=1)
        joule=float(sum(sigma*area[plate]/12*(np.sum(D[plate]**2,axis=1)+np.sum(D[plate],axis=1)**2)))*height
        force=-sigma*area[plate,None]*meanD[plate,None]*ga[plate];Fx,Fy=np.sum(force,axis=0)*height
        power=float(sum(area*Js*At[tri].mean(axis=1)))*height;fieldwork=float(sum(area*nu*np.einsum('ti,ti->t',ga,delta_grad)))*height;stored=float(sum(area*W))*height
        algorithmic=fieldwork-(stored-lastW)/dt;balance=power-fieldwork-joule-speed*Fx
        rows.append(dict(time_s=time,Newton_iterations=iteration,nonlinear_residual_relative=float(np.linalg.norm(R)/scale),
            source_field_W=power,secondary_Joule_W=joule,thrust_N=float(Fx),normal_force_N=float(Fy),mechanical_W=float(speed*Fx),magnetic_energy_J=stored,
            magnetic_discrete_work_W=fieldwork,backward_Euler_dissipation_W=algorithmic,discrete_power_residual_W=float(balance),
            net_secondary_current_A=float(-sigma*sum(area[plate]*meanD[plate])),floating_u_V_m=float(u),peak_steel_B_T=float(max(B[regions==3]))))
        if progress:progress(rows[-1])
        lastW=stored
    return dict(trace=rows,final_A_Wb_m=A.tolist(),final_u_V_m=float(u),Peclet_max=Pe,nodes=N,elements=len(tri),magnetic_energy_initial_J=initialW,
        last_period_mean={key:float(np.mean([row[key] for row in rows[-c['steps_per_period']:]])) for key in ('thrust_N','normal_force_N','source_field_W','secondary_Joule_W','mechanical_W','backward_Euler_dissipation_W')},
        numerical_scope='Backward Euler/P1 Galerkin frozen-mask nonlinear current excitation; independent convergence and physical correlation still required')


def benchmark_plan():
    jobs=[dict(id='zero-current',case=case(current_peak_A=0.)),dict(id='linear-moving-limit',case=case(current_peak_A=25.,linear=True)),
        dict(id='nonlinear-frozen-v10',case=case()),dict(id='nonlinear-dt-half',case=case(steps_per_period=64)),
        dict(id='stationary-forward-phase',case=case(speed_m_s=0.)),dict(id='stationary-reverse-phase',case=case(speed_m_s=0.,phase_direction=-1))]
    result=dict(schema='osr-transient-LIM-method-plan/1',jobs=jobs,maximum_jobs=6,timeout_s=90,memory_mb=3072,
        independent_controls=['Constitutive H(B), tangent and stored-energy derivative versus inverse tabulation',
            'Linear moving periodic limit versus retained identical-geometry phasor solve, not arbitrary force scaling',
            'Generic nonlinear DC material/circuit against existing independent scalar/GetDP circuit benchmark',
            'Zero/current phase-reversal, net-current closure, discrete work and positive BE dissipation',
            'Time/mesh/outer-boundary refinement; frozen-mask velocity is not a transit model'],
        primary_reference='https://getdp.info/doc/texinfo/getdp.html#Nonlinear-resolution',scope=SCOPE,
        installed_available_force_N=None,nonlinear_operating_map_available=False,**FLAGS)
    result['plan_id']=identity(result);return result


def run(c,output,*,root=ROOT):
    output=Path(output).resolve();root=Path(root).resolve()
    if output.exists():raise ValueError('Fresh immutable transient package required')
    validate_case(c)
    sources=source_map(root,PRODUCERS)
    if digest(__file__)!=sources[PRODUCER] or any(digest(module.__file__)!=sources[name] for module,name in ((long_motor,long_motor.PRODUCER),(station_motor,station_motor.PRODUCER),(lim_materials,'engineering/design_search/lim_materials.py'))):raise ValueError('Loaded producer differs from declared root source')
    output.mkdir(parents=True);d=definition(c);curve=lim_materials.material()
    (output/'input.json').write_bytes(encoded(dict(case=c,definition=d,material=curve,source_sha256=sources)))
    cap=min([3*1024**3,*[n for n in resource.getrlimit(resource.RLIMIT_AS) if n!=resource.RLIM_INFINITY]])
    def limit():resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    tool=dict(python_sha256=digest(sys.executable),timeout_s=90,RLIMIT_AS_bytes=cap,threads=1)
    try:
        proc=subprocess.run([sys.executable,'-m','engineering.design_search.transient_lim','--worker',str(output)],cwd=root,capture_output=True,timeout=90,preexec_fn=limit,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        stdout,stderr=proc.stdout,proc.stderr
        if (output/'worker-result.json').is_file():r=json.loads((output/'worker-result.json').read_bytes())
        else:r=dict(execution='tool_error',reason='Worker returned '+str(proc.returncode),numerical_validity='unknown')
    except subprocess.TimeoutExpired as error:
        stdout,stderr=error.stdout or b'',error.stderr or b''
        r=dict(execution='interrupted',reason='90s process budget exceeded; raw partial trace retained',numerical_validity='unknown')
    (output/'stdout.log').write_bytes(stdout);(output/'stderr.log').write_bytes(stderr)
    if source_map(root,PRODUCERS)!=sources:raise ValueError('Transient producer/source changed')
    r.update(schema='osr-transient-frozen-LIM-2D/1',case=c,motor_component_id=d['motor_component_id'],source_sha256=sources,tool=tool,scope=SCOPE,engineering_screen='unknown',time_refinement='not-run',mesh_refinement='not-run',primary_copper_W=None,inverter_terminal_power_W=None,temperature_C=None,
        selected_supplier_steel_qualified=False,moving_geometry_simulated=False,installed_available_force_N=None,nonlinear_operating_map_available=False,**FLAGS)
    r['evaluation_id']=identity(r);(output/'result.json').write_bytes(encoded(r));m=dict(evaluation_id=r['evaluation_id'],source_sha256=sources,files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()},**FLAGS);m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return r


def verify(output,*,root=ROOT):
    output=Path(output);root=Path(root)
    manifest=json.loads((output/'manifest.json').read_bytes());result=json.loads((output/'result.json').read_bytes());data=json.loads((output/'input.json').read_bytes())
    if manifest['manifest_id']!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('Transient manifest identity differs')
    if result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'}) or result['evaluation_id']!=manifest['evaluation_id']:raise ValueError('Transient evaluation identity differs')
    if {p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}!=manifest['files_sha256']:raise ValueError('Transient payload differs')
    if source_map(root,PRODUCERS)!=manifest['source_sha256'] or result['source_sha256']!=manifest['source_sha256'] or data['source_sha256']!=manifest['source_sha256']:raise ValueError('Transient source/context differs')
    validate_case(data['case'])
    if data['definition']!=definition(data['case']) or result['motor_component_id']!=data['definition']['motor_component_id']:raise ValueError('Transient physical fixture identity differs')
    if result['case']!=data['case'] or any(result.get(k) is not v or manifest.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Transient research identity/release flags differ')
    if result.get('installed_available_force_N') is not None or result.get('nonlinear_operating_map_available') is not False or result.get('moving_geometry_simulated') is not False:raise ValueError('Method evidence cannot become available operating force')
    return dict(verified=True,evaluation_id=result['evaluation_id'],physical_accepted=False)


def _worker(folder):
    folder=Path(folder);data=json.loads((folder/'input.json').read_bytes());deadline=monotonic()+85
    try:
        validate_case(data['case'])
        expected=definition(data['case'])
        if data['definition']!=expected or data['material']!=lim_materials.material() or source_map(ROOT,PRODUCERS)!=data['source_sha256']:raise ValueError('Transient input producer/material/definition differs')
        meta=long_motor.mesh(folder,data['case'],data['definition']);points,tri,regions,boundary=read_mesh(folder/'motor.msh')
        if len(points)>data['case']['maximum_nodes']:raise ValueError('Mesh node budget exceeded')
        def progress(row):
            with (folder/'partial-trace.jsonl').open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
        r=solve(points,tri,regions,boundary,data['case'],data['definition'],data['material'],deadline=deadline,progress=progress)
        import gmsh
        import scipy.sparse.linalg._dsolve._superlu as superlu
        r.update(execution='completed',numerical_validity='unconfirmed',mesh=meta,software=dict(numpy=np.__version__,scipy=scipy.__version__,superlu_binary_sha256=digest(superlu.__file__),gmsh_python_sha256=digest(gmsh.__file__),gmsh_library_sha256=digest(gmsh.libpath)))
    except Exception as error:r=dict(execution='interrupted' if isinstance(error,TimeoutError) else 'refused',numerical_validity='unknown',reason=str(error))
    (folder/'worker-result.json').write_bytes(encoded(r))


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='--worker':raise SystemExit('Use run(case,output); worker entry is internal')
    _worker(sys.argv[2])
