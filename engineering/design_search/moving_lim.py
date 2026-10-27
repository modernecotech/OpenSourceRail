"""Finite travelling-secondary A/u and voltage-circuit component research.

The aluminium rectangle really translates through a fixed primary mesh. Exact
cut-triangle moments replace a frozen conductor mask; no force/overlap scaling
is used. This remains a 2D, reversible-steel, prescribed-speed component model.
Finite-height return currents, real winding connections/leakage, controllers,
supplier steel, converter loss and repeated thermal duty remain unqualified.
"""
from copy import deepcopy
from pathlib import Path
from math import ceil, pi, sqrt, isfinite
from time import monotonic
from hashlib import sha256
import json, os, resource, subprocess, sys
import numpy as np
import scipy
from scipy.sparse import coo_matrix, csr_matrix, bmat, diags
from scipy.sparse.linalg import spsolve
from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import identity, digest, encoded
from . import wheel_motor, railway_bundle, transient_lim, lim_materials, lim_transport, lim_critical_mesh

CODE='engineering/design_search/moving_lim.py'
REFERENCE='https://github.com/getdp-project/getdp/blob/master/templates/Lib_Magnetodynamics2D_av_Cir.pro'
SCOPE='Finite translating 9m secondary and exact canonical primary cross-section; 2D A/u, declared winding wiring and ideal voltage source; component research only'


def wiring_definition():
    return dict(hypothesis='round-robin side-period pairs into ten paths per phase; five coils in series per path',
        branches=30,coils_per_path=5,coil_count=150,neutral='floating; total branch current zero',
        actual_connection_verified=False,external_leakage_inductance_H_hypothesis=0.,actual_external_leakage_H=None)


def request(bundle,*,start_m=-8.95,speed_m_s=.5,voltage_peak_V=2.,frequency_Hz=30.,
            dt_s=.002,steps=20,mesh_m=.04,temperature_C=80.,current_limit_A=140.,linear=False,transport_method='galerkin',
            mesh_family='legacy-tensor',critical_dx_m=None,secondary_dy_m=None):
    railway_bundle.validate(bundle)
    if bundle['family_id']!='P1' or bundle['motor_parameters'] is None:raise ValueError('Exact P1 canonical motor bundle required')
    definition=wheel_motor.definition(bundle['motor_parameters'])
    if definition!=bundle['motor_definition'] or definition['motor_component_id']!=bundle['propulsion_component_id']:raise ValueError('Canonical motor geometry differs')
    values=(start_m,speed_m_s,voltage_peak_V,frequency_Hz,dt_s,mesh_m,current_limit_A)
    if any(type(v) not in (float,int) or not isfinite(v) for v in values):raise ValueError('Finite component evaluation hypotheses required')
    if abs(speed_m_s)>20 or not 0<=voltage_peak_V<=375 or not 1<=frequency_Hz<=100 or not .00005<=dt_s<=.01 or not .005<=mesh_m<=.08 or not 0<current_limit_A<=140:raise ValueError('Declared voltage/current/mesh/time domain exceeded')
    if frequency_Hz*dt_s>=.5:raise ValueError('Nyquist sampling requires frequency_Hz*dt_s < 0.5; this is not a convergence criterion')
    if type(steps) is not int or not 1<=steps<=128 or temperature_C not in (20.,80.) or type(linear) is not bool:raise ValueError('Bounded time/material hypothesis required')
    p=definition['physical_configuration'];paths=p['parallel_paths_per_phase']
    if paths!=10 or p['periods']!=25:raise ValueError('Only explicit reference 25-period/10-path wiring experiment supported')
    finish=start_m+speed_m_s*dt_s*steps
    if not -p['secondary_length_m']-.5<=min(start_m,finish) or max(start_m,finish)>p['primary_length_m']+.5:
        raise ValueError('Translation outside bounded entry/exit construction domain')
    wiring=wiring_definition()
    transport=lim_transport.method(transport_method)
    r=dict(schema='osr-moving-LIM-request/2',bundle_id=bundle['candidate_id'],bundle_definition_id=bundle['definition_id'],bundle_definition=deepcopy(bundle),
        body_candidate_id=bundle['body_candidate_id'],motor_component_id=definition['motor_component_id'],motor_definition=definition,
        physical_geometry=deepcopy(p),wiring=wiring,wiring_hypothesis_id=identity(wiring),start_m=start_m,speed_m_s=speed_m_s,
        voltage_peak_V=voltage_peak_V,frequency_Hz=frequency_Hz,dt_s=dt_s,steps=steps,mesh_m=mesh_m,
        temperature_C=temperature_C,current_limit_A=current_limit_A,linear=linear,dc_bus_V_hypothesis=750.,
        transport_method=transport,maximum_nodes=75000,maximum_seconds=85.,memory_bytes=2*1024**3,
        actual_converter_loss_W=None,actual_cooling_W=None,repeated_thermal_duty_verified=False,
        available_operating_map=None,complete_installed_mass_kg=None,references=[REFERENCE,lim_transport.REFERENCE],scope=SCOPE,**FLAGS)
    r['evaluated_component_definition_id']=identity(dict(motor_geometry_id=definition['motor_component_id'],wiring_hypothesis=wiring))
    if mesh_family==lim_critical_mesh.NAME:
        if mesh_m!=.04:raise ValueError('Local mesh family uses explicit critical targets; retain the legacy mesh mirror at .04m')
        r['schema']='osr-moving-LIM-request/3'
        r['mesh_definition']=lim_critical_mesh.definition(.02 if critical_dx_m is None else critical_dx_m,.00375 if secondary_dy_m is None else secondary_dy_m)
        r['operating_hypothesis']=dict(phase_frequency_Hz=frequency_Hz,nominal_synchronous_speed_m_s=frequency_Hz*definition['wavelength_m'],
            nominal_slip_frequency_Hz=frequency_Hz-speed_m_s/definition['wavelength_m'],transient_force_sign_guaranteed=False,
            actual_propulsion_capability_verified=False)
        lim_critical_mesh.axes(r)
    elif mesh_family!='legacy-tensor' or critical_dx_m is not None or secondary_dy_m is not None:
        raise ValueError('Explicit supported mesh family and matching numerical variables required')
    r['request_id']=identity(r);return r


def validate(r):
    if not isinstance(r,dict) or not isinstance(r.get('bundle_definition'),dict):raise ValueError('Complete moving request and canonical bundle required')
    mesh_arguments={}
    if r.get('schema')=='osr-moving-LIM-request/3':
        d=r.get('mesh_definition')
        if not isinstance(d,dict) or 'critical_dx_m' not in d or 'secondary_dy_m' not in d:raise ValueError('Explicit critical mesh definition required')
        mesh_arguments=dict(mesh_family=lim_critical_mesh.NAME,critical_dx_m=d['critical_dx_m'],secondary_dy_m=d['secondary_dy_m'])
    if set(r)!=set(request(r['bundle_definition'],**mesh_arguments)):raise ValueError('Moving request schema fields differ from bounded constructor')
    if r.get('request_id')!=identity({k:v for k,v in r.items() if k!='request_id'}):raise ValueError('Moving request identity differs')
    railway_bundle.validate(r['bundle_definition'])
    if r['bundle_definition']['candidate_id']!=r['bundle_id'] or r['bundle_definition']['definition_id']!=r['bundle_definition_id'] or r['bundle_definition']['propulsion_component_id']!=r['motor_component_id'] or r['bundle_definition']['body_candidate_id']!=r['body_candidate_id']:raise ValueError('Moving request mixed physical bundle')
    d=wheel_motor.definition(dict(physical=r['physical_geometry'],evaluation=wheel_motor.default_parameters()['evaluation']))
    if d!=r['motor_definition'] or d['motor_component_id']!=r['motor_component_id']:raise ValueError('Moving physical definition differs from exact motor')
    if r['physical_geometry']!=wheel_motor.default_parameters()['physical']:raise ValueError('This evaluator currently supports the explicit reference geometry only')
    if r['maximum_nodes']!=75000 or r['memory_bytes']!=2*1024**3 or not 0<r['maximum_seconds']<=85:raise ValueError('Moving resource contract differs')
    if r['wiring']!=wiring_definition() or r['wiring_hypothesis_id']!=identity(r['wiring']):raise ValueError('Moving wiring hypothesis differs')
    if r['evaluated_component_definition_id']!=identity(dict(motor_geometry_id=r['motor_component_id'],wiring_hypothesis=r['wiring'])):raise ValueError('Moving electrical component definition differs')
    if not 1<=r['steps']<=128 or type(r['steps']) is not int or not .00005<=r['dt_s']<=.01 or not .005<=r['mesh_m']<=.08:raise ValueError('Bounded step/mesh contract differs')
    if not 0<=r['voltage_peak_V']<=r['dc_bus_V_hypothesis']/2 or r['dc_bus_V_hypothesis']!=750 or not 0<r['current_limit_A']<=140 or abs(r['speed_m_s'])>20:raise ValueError('Electrical or velocity domain differs')
    if r['temperature_C'] not in (20.,80.) or type(r['linear']) is not bool:raise ValueError('Declared material hypothesis differs')
    if r['wiring']['external_leakage_inductance_H_hypothesis']!=0 or r['wiring']['actual_external_leakage_H'] is not None:raise ValueError('External leakage is an unresolved idealization, not an installed value')
    if any(r.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Component research cannot grant acceptance')
    # Reconstruct the entire public request rather than maintaining a second,
    # partial list of domains. This also binds all uncertainty/disposition fields
    # and prevents a resealed record from claiming a different body or method.
    keys=('start_m','speed_m_s','voltage_peak_V','frequency_Hz','dt_s','steps','mesh_m','temperature_C','current_limit_A','linear')
    if not isinstance(r['transport_method'],dict) or r['transport_method']!=lim_transport.method(r['transport_method'].get('name')):raise ValueError('Moving transport method differs')
    expected=request(r['bundle_definition'],**{key:r[key] for key in keys},transport_method=r['transport_method']['name'],**mesh_arguments)
    if r!=expected:raise ValueError('Moving request differs from bounded constructor and model domain')


def _subdivide(edges,h):
    edges=sorted(set(round(float(x),12) for x in edges));out=[]
    for a,b in zip(edges,edges[1:]):out.extend(np.linspace(a,b,max(1,ceil((b-a)/h))+1)[:-1])
    return np.r_[out,edges[-1]]


def _mesh_axes(r):
    if r.get('schema')=='osr-moving-LIM-request/3':return lim_critical_mesh.axes(r)
    p=r['physical_geometry'];L=p['primary_length_m'];pitch=2*p['pole_pitch_m']/6
    end=r['start_m']+r['speed_m_s']*r['dt_s']*r['steps'];fin=p['secondary_length_m']
    lo=min(-.5,r['start_m']-.5,end-.5);hi=max(L+.5,r['start_m']+fin+.5,end+fin+.5)
    xedges=[lo,0.,L,hi]
    for k in range(p['periods']*6):
        x=(k+.5)*pitch;xedges.extend([x-p['slot_width_m']/2,x+p['slot_width_m']/2])
    x=_subdivide(xedges,r['mesh_m']);half=p['secondary_thickness_m']/2;face=half+p['gap_each_side_m'];back=face+p['slot_depth_m'];outer=back+p['backiron_m']
    y=_subdivide([-outer-.2,-outer,-back,-face,-half,0.,half,face,back,outer,outer+.2],min(.02,r['mesh_m']/2))
    # Four material-aligned layers across secondary and each physical air gap.
    y=np.unique(np.r_[y,np.linspace(-face,face,1+12*max(1,ceil(.04/r['mesh_m'])))])
    return x,y


def estimate(r):
    """Necessary construction/transport screens before allocating field arrays."""
    validate(r);x,y=_mesh_axes(r);half=r['physical_geometry']['secondary_thickness_m']/2
    band=y[(y>=-half-1e-12)&(y<=half+1e-12)]
    d=r['motor_definition'];sigma=d['aluminium_conductivity_20C_S_m_hypothesis'] if r['temperature_C']==20 else d['aluminium_conductivity_80C_S_m_hypothesis']
    dx=float(max(np.diff(x)));dy=float(max(np.diff(band)));Pe=abs(r['speed_m_s'])*sqrt(dx*dx+dy*dy)*transient_lim.MU0*sigma/2
    nodes=len(x)*len(y)
    result=dict(nodes=nodes,elements=2*(len(x)-1)*(len(y)-1),Peclet_max=Pe,
        max_streamwise_cell_m=dx,mesh_nodes_within_budget=nodes<=r['maximum_nodes'],
        unstabilized_domain_supported=Pe<=1,transport_method_id=r['transport_method']['method_id'],
        estimated_actual_RAM_bytes=None,enforced_address_space_limit_bytes=r['memory_bytes'])
    if r.get('schema')=='osr-moving-LIM-request/3':result['active_grid']=lim_critical_mesh.diagnostics(r,x,y)
    return result


def mesh(r):
    """Conform every fixed tooth/slot and every transverse material boundary."""
    x,y=_mesh_axes(r);p=r['physical_geometry'];L=p['primary_length_m'];pitch=2*p['pole_pitch_m']/6
    face=p['secondary_thickness_m']/2+p['gap_each_side_m'];back=face+p['slot_depth_m'];outer=back+p['backiron_m']
    if len(x)*len(y)>r['maximum_nodes']:raise ValueError('Necessary mesh node bound exceeded before allocation')
    points=np.array([(a,b) for a in x for b in y]);ny=len(y);tri=[]
    for i in range(len(x)-1):
        for j in range(ny-1):
            a=i*ny+j;b=a+ny;tri.extend([(a,b,b+1),(a,b+1,a+1)])
    tri=np.asarray(tri,dtype=int);centers=points[tri].mean(axis=1);regions=np.ones(len(tri),dtype=int)
    iron=(centers[:,0]>0)&(centers[:,0]<L)&(abs(centers[:,1])>face)&(abs(centers[:,1])<outer);regions[iron]=3
    paths=p['parallel_paths_per_phase'];branch=np.full(len(tri),-1,dtype=int);sign=np.zeros(len(tri))
    for k in range(p['periods']*6):
        inside=iron&(abs(centers[:,0]-(k+.5)*pitch)<p['slot_width_m']/2)&(abs(centers[:,1])<back)
        phase=(0,2,1,0,2,1)[k%6];sgn=(1,-1,1,-1,1,-1)[k%6]
        for side in (-1,1):
            rows=inside&(centers[:,1]*side>0);period=k//6;coil_index=(0 if side<0 else 25)+period
            branch[rows]=phase*paths+coil_index%paths;sign[rows]=sgn;regions[rows]=100+phase
    boundary=np.flatnonzero((points[:,0]==x[0])|(points[:,0]==x[-1])|(points[:,1]==y[0])|(points[:,1]==y[-1]))
    return points,tri,regions,boundary,branch,sign


def mesh_fingerprint(points,tri,regions,boundary,branch,sign):
    """Actual assembled mesh identity, independent of physical candidate IDs."""
    arrays=dict(points=(points,'<f8'),triangles=(tri,'<i8'),regions=(regions,'<i8'),
        boundary=(boundary,'<i8'),winding_branch=(branch,'<i8'),winding_sign=(sign,'<f8'))
    record={name:dict(shape=list(np.asarray(a).shape),dtype=kind,sha256=sha256(np.asarray(a,dtype=kind).tobytes()).hexdigest()) for name,(a,kind) in arrays.items()}
    record['mesh_discretization_id']=identity(record);return record


def clipped_moments(vertices,start,end):
    """Exact degree-two P1 moments on a triangle clipped by two moving faces."""
    polygon=[v.copy() for v in vertices]
    for edge,sgn in ((start,1),(end,-1)):
        result=[]
        for a,b in zip(polygon,polygon[1:]+polygon[:1]):
            ina=sgn*(a[0]-edge)>=0;inb=sgn*(b[0]-edge)>=0
            if ina:result.append(a)
            if ina!=inb:result.append(a+(b-a)*((edge-a[0])/(b[0]-a[0])))
        polygon=result
        if not polygon:break
    m0=0.;m1=np.zeros(3);m2=np.zeros((3,3));inverse=np.linalg.inv(np.c_[np.ones(3),vertices])
    for k in range(1,len(polygon)-1):
        sub=np.array([polygon[0],polygon[k],polygon[k+1]])
        area=abs(np.linalg.det(np.array([sub[1]-sub[0],sub[2]-sub[0]])))/2
        bary=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])
        N=np.c_[np.ones(3),bary@sub]@inverse
        m0+=area;m1+=area*N.mean(axis=0);m2+=area*N.T@N/3
    return m0,m1,m2


def conductor_moments(points,tri,area,start,length,thickness):
    v=points[tri];m0=np.zeros(len(tri));m1=np.zeros((len(tri),3));m2=np.zeros((len(tri),3,3));end=start+length
    band=np.max(abs(v[:,:,1]),axis=1)<=thickness/2+1e-12
    active=band&(v[:,:,0].max(axis=1)>start)&(v[:,:,0].min(axis=1)<end)
    full=active&(v[:,:,0].min(axis=1)>=start)&(v[:,:,0].max(axis=1)<=end)
    m0[full]=area[full];m1[full]=area[full,None]/3;m2[full]=area[full,None,None]*(np.eye(3)+np.ones((3,3)))/12
    for k in np.flatnonzero(active&~full):m0[k],m1[k],m2[k]=clipped_moments(v[k],start,end)
    return m0,m1,m2


def net_secondary_current(sigma,m1,D):
    """Integral J_z dx dy in amperes; no extrusion-height multiplier."""
    return float(-sigma*np.einsum('ti,ti->',m1,D))


def circuit_jacobian(K,b,closure,S,W,R,dt,height,*,field_b=None):
    """Reciprocal stranded-winding coupling, floating plate and star neutral.

    K already contains the field tangent plus conductivity/time/transport terms.
    Field equations are per extrusion metre; circuit flux linkage includes the
    exact active height, so terminal work and field work have consistent units.
    """
    nf,nc=W.shape;z=csr_matrix((nf,1));z1=csr_matrix((1,1));zi=csr_matrix((1,nc))
    field_b=b if field_b is None else field_b
    return bmat([[K,csr_matrix(field_b[:,None]),-W,z],
        [csr_matrix((b/dt+closure)[None,:]),csr_matrix([[S]]),zi,z1],
        [height*W.T/dt,csr_matrix((nc,1)),diags(R),csr_matrix(np.ones((nc,1)))],
        [z.T,z1,csr_matrix(np.ones((1,nc))),z1]],format='csc')


def solve(r,*,progress=None):
    validate(r);started=monotonic();bounds=estimate(r)
    if not bounds['mesh_nodes_within_budget']:raise ValueError('Necessary mesh node bound exceeded before allocation')
    if not bounds['unstabilized_domain_supported'] and r['transport_method']['name']=='galerkin':raise ValueError('Unstabilized conductor Peclet>1; independently validated refinement/stabilization required')
    points,tri,regions,boundary,branch,sign=mesh(r)
    actual_mesh=mesh_fingerprint(points,tri,regions,boundary,branch,sign)
    area,grad=transient_lim.geometry(points,tri);N=len(points);free=np.setdiff1d(np.arange(N),boundary);nf=len(free);nc=30
    rr=np.repeat(tri,3,axis=1).ravel();cc=np.tile(tri,(1,3)).ravel()
    def matrix(v):return coo_matrix((v.ravel(),(rr,cc)),shape=(N,N)).tocsr()
    p=r['physical_geometry'];d=r['motor_definition'];h=p['active_height_m'];dt=r['dt_s'];v=r['speed_m_s']
    # Unstabilized transport must be resolved; numerical budget cannot weaken it.
    band=np.max(abs(points[tri][:,:,1]),axis=1)<=p['secondary_thickness_m']/2+1e-12
    lengths=np.max(np.linalg.norm(points[tri][:,:,None,:]-points[tri][:,None,:,:],axis=-1),axis=(1,2))
    sigma=d['aluminium_conductivity_20C_S_m_hypothesis'] if r['temperature_C']==20 else d['aluminium_conductivity_80C_S_m_hypothesis']
    pe=float(np.max(lengths[band])*abs(v)*transient_lim.MU0*sigma/2)
    if pe>1 and r['transport_method']['name']=='galerkin':raise ValueError('Unstabilized conductor Peclet>1; independently validated refinement/stabilization required')
    coil=np.flatnonzero(branch>=0);ww=[];wr=[];wc=[]
    for k in coil:
        for node in tri[k]:wr.append(node);wc.append(branch[k]);ww.append(area[k]*p['turns_per_coil']*sign[k]/(3*p['slot_width_m']*p['slot_depth_m']))
    W=coo_matrix((ww,(wr,wc)),shape=(N,nc)).tocsr();Wf=W[free]
    rho=d['copper_resistivity_20C_ohm_m_hypothesis']*(1+d['copper_temperature_coefficient_K_inv_hypothesis']*(r['temperature_C']-20))
    R=np.full(nc,5*rho*d['wire_length_m_per_coil']/p['conductor_area_m2'])
    A=np.zeros(N);I=np.zeros(nc);u=neutral=0.;rows=[];last_energy=0.;curve=lim_materials.material();state='completed'
    for step in range(1,r['steps']+1):
        if monotonic()-started>r['maximum_seconds']:raise TimeoutError('Moving component numerical time budget exceeded')
        old=A.copy();oldI=I.copy();time=step*dt;start=r['start_m']+v*time
        m0,m1,m2=conductor_moments(points,tri,area,start,p['secondary_length_m'],p['secondary_thickness_m'])
        if abs(m0.sum()-p['secondary_length_m']*p['secondary_thickness_m'])>1e-9:raise ValueError('Moving conductor volume lost or duplicated')
        M=matrix(sigma*m2);C=matrix(sigma*v*m1[:,:,None]*grad[:,None,:,0]);b=np.bincount(tri.ravel(),weights=(sigma*m1).ravel(),minlength=N);closure=np.asarray(C.sum(axis=0)).ravel();S=sigma*m0.sum()
        stabilization=lim_transport.operators(m0,m1,grad[:,:,0],sigma=sigma,speed=v,diffusivity=1/(transient_lim.MU0*sigma),name=r['transport_method']['name'])
        Ms=matrix(stabilization['mass']);Cs=matrix(stabilization['transport']);bs=np.bincount(tri.ravel(),weights=stabilization['floating'].ravel(),minlength=N)
        command=np.repeat(r['voltage_peak_V']*np.cos(2*pi*r['frequency_Hz']*time-np.arange(3)*2*pi/3),10)
        for iteration in range(24):
            local,jac,ga,B,nu,energy_density=transient_lim.magnetic(A,tri,area,grad,regions,curve,r['linear'])
            At=(A-old)/dt;fa=np.bincount(tri.ravel(),weights=local.ravel(),minlength=N)+(M+Ms)@At+(C+Cs)@A+(b+bs)*u-W@I
            residual=np.r_[fa[free],b@At+closure@A+S*u,R*I+h*(W.T@At)+neutral-command,I.sum()]
            norm=float(np.linalg.norm(residual))
            if norm<1e-8*max(1.,np.linalg.norm(command)):break
            K=matrix(jac)+(M+Ms)/dt+C+Cs
            J=circuit_jacobian(K[free][:,free],b[free],closure[free],S,Wf,R,dt,h,field_b=(b+bs)[free])
            delta=spsolve(J,-residual)
            if np.any(~np.isfinite(delta)):raise ValueError('Nonfinite coupled field/circuit update')
            A[free]+=delta[:nf];u+=delta[nf];I+=delta[nf+1:nf+1+nc];neutral+=delta[-1]
        else:raise ValueError('Coupled field/circuit nonlinear solve did not converge')
        At=(A-old)/dt;D=At[tri]+u+v*ga[:,0,None];integralD=np.einsum('ti,ti->t',m1,D)
        heat=float(sigma*np.einsum('ti,tij,tj->',D,m2,D)*h);force=-sigma*np.sum(integralD[:,None]*ga,axis=0)*h
        copper=float(np.sum(R*I*I));terminal=float(command@I);stored=float(np.sum(area*energy_density)*h)
        grad_delta=np.einsum('ti,tij->tj',(A-old)[tri],grad)
        field_work=float(np.sum(area*nu*np.einsum('ti,ti->t',ga,grad_delta))*h/dt)
        algorithmic=field_work-(stored-last_energy)/dt
        stabilization_W=lim_transport.power(At[tri],A[tri],u,stabilization,h)
        residual_W=terminal-copper-heat-float(v*force[0])-field_work-stabilization_W
        row=dict(time_s=time,secondary_start_m=start,secondary_end_m=start+p['secondary_length_m'],
            overlap_primary_m=max(0.,min(start+p['secondary_length_m'],p['primary_length_m'])-max(0.,start)),
            conductor_area_m2=float(m0.sum()),conductor_first_moment_x_m3=float(sum(np.einsum('ti,ti->t',m1,points[tri][:,:,0]))),
            path_currents_A=I.tolist(),phase_voltage_commands_V=command[::10].tolist(),neutral_voltage_V=float(neutral),
            terminal_W=terminal,primary_copper_W=copper,secondary_Joule_W=heat,thrust_N=float(force[0]),normal_force_N=float(force[1]),
            mechanical_W=float(v*force[0]),magnetic_energy_J=stored,backward_Euler_dissipation_W=float(algorithmic),
            stabilization_work_W=stabilization_W,stabilization_work_is_physical_heat=False,
            discrete_power_residual_W=float(residual_W),net_secondary_current_A=net_secondary_current(sigma,m1,D),
            net_terminal_current_A=float(I.sum()),peak_steel_B_T=float(max(B[regions==3])),coupled_residual=norm,Newton_iterations=iteration)
        rows.append(row)
        if progress:progress(row)
        last_energy=stored
        if max(abs(I))>r['current_limit_A']:state='current-limit';break
        if r['linear'] and row['peak_steel_B_T']>1.3:state='outside-linear-steel-domain';break
    return dict(execution='completed',state=state,trace=rows,nodes=N,elements=len(tri),Peclet_max=pe,mesh_diagnostics=bounds.get('active_grid'),actual_mesh=actual_mesh,
        final_A_sha256=identity(A.tolist()),final_current_A=I.tolist(),
        moving_geometry_simulated=True,current_circuit_coupled=True,wire_resistance_ohm_per_path=R.tolist(),transport_method=r['transport_method'],
        available_operating_map=None,actual_converter_loss_W=None,temperature_C_prediction=None,
        repeated_thermal_duty_verified=False,finite_height_return_current_verified=False,
        installed_force_available_N=None,numerical_validity='algebraic-residuals-evaluated-spatial-time-convergence-unconfirmed',
        engineering_screen='unknown' if state=='completed' else 'failed-declared-component-screen',**FLAGS)


def sources(root=ROOT):
    names=(CODE,lim_critical_mesh.CODE,lim_transport.CODE,wheel_motor.PRODUCER,transient_lim.PRODUCER,'engineering/design_search/lim_materials.py',lim_materials.DATA,
           'engineering/design_search/railway_bundle.py','engineering/station_rail/common.py','engineering/station_rail/station_motor.py')
    return {name:digest(Path(root)/name) for name in names}


def run(r,output,*,root=ROOT):
    validate(r);root=Path(root).resolve();out=Path(output).resolve()
    if out.exists():raise ValueError('Fresh immutable moving component run required')
    source=sources(root)
    if source[CODE]!=digest(__file__):raise ValueError('Executing moving evaluator differs from source root')
    out.mkdir(parents=True);(out/'input.json').write_bytes(encoded(dict(request=r,source_sha256=source)))
    def limit():resource.setrlimit(resource.RLIMIT_AS,(r['memory_bytes'],r['memory_bytes']))
    try:
        p=subprocess.run([sys.executable,'-m','engineering.design_search.moving_lim','--worker',str(out)],cwd=root,
            capture_output=True,timeout=90,preexec_fn=limit,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
        (out/'stdout.log').write_bytes(p.stdout);(out/'stderr.log').write_bytes(p.stderr)
        result=json.loads((out/'worker-result.json').read_bytes()) if (out/'worker-result.json').is_file() else dict(execution='tool-error',reason='Worker returned '+str(p.returncode),**FLAGS)
    except subprocess.TimeoutExpired as e:
        (out/'stdout.log').write_bytes(e.stdout or b'');(out/'stderr.log').write_bytes(e.stderr or b'')
        result=dict(execution='interrupted',reason='90s subprocess budget exceeded; partial trace preserved',**FLAGS)
    if sources(root)!=source:raise ValueError('Moving evaluator source changed during run; unsealed logs retained')
    result.update(request_id=r['request_id'],bundle_id=r['bundle_id'],motor_component_id=r['motor_component_id'],
        evaluated_component_definition_id=r['evaluated_component_definition_id'],canonical_interface_qualification='held-unverified-wiring-3D-and-thermal',
        source_sha256=source,scope=SCOPE,evidence_kind='conditional-moving-component-method',operating_map_admitted=False)
    result['evaluation_id']=identity(result);(out/'result.json').write_bytes(encoded(result))
    manifest=dict(evaluation_id=result['evaluation_id'],files_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},source_sha256=source,**FLAGS)
    manifest['manifest_id']=identity(manifest);(out/'manifest.json').write_bytes(encoded(manifest));return result


def verify(output,*,root=ROOT):
    out=Path(output);m=json.loads((out/'manifest.json').read_bytes());r=json.loads((out/'result.json').read_bytes());data=json.loads((out/'input.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}) or r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Moving package identity differs')
    if m['evaluation_id']!=r['evaluation_id']:raise ValueError('Moving manifest/result evaluation identity differs')
    if {p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Moving package payload differs')
    if sources(root)!=m['source_sha256'] or r['source_sha256']!=m['source_sha256'] or data['source_sha256']!=m['source_sha256']:raise ValueError('Moving package source epoch differs')
    validate(data['request'])
    if r['request_id']!=data['request']['request_id'] or r['motor_component_id']!=data['request']['motor_component_id'] or r['bundle_id']!=data['request']['bundle_id']:raise ValueError('Moving package physical/context identity differs')
    if r.get('operating_map_admitted') is not False or any(r.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Moving component cannot claim operating acceptance')
    return dict(verified=True,evaluation_id=r['evaluation_id'],verifier_sha256=digest(__file__),
        numerical_source_sha256=m['source_sha256'],physical_accepted=False)


def _worker(folder):
    out=Path(folder);data=json.loads((out/'input.json').read_bytes())
    try:
        if sources()!=data['source_sha256']:raise ValueError('Moving worker source epoch differs')
        def progress(row):
            with (out/'partial-trace.jsonl').open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
        result=solve(data['request'],progress=progress)
    except Exception as e:result=dict(execution='interrupted' if isinstance(e,TimeoutError) else 'held',reason=type(e).__name__+': '+str(e),**FLAGS)
    import scipy.sparse.linalg._dsolve._superlu as superlu
    result['tool']=dict(python=sys.version,python_sha256=digest(sys.executable),numpy=np.__version__,scipy=scipy.__version__,superlu_sha256=digest(superlu.__file__),threads=1,memory_bytes=2*1024**3)
    (out/'worker-result.json').write_bytes(encoded(result))


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='--worker':raise SystemExit('Internal bounded worker; use moving_lim.request and run')
    _worker(sys.argv[2])
