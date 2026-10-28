"""Revised-resource derivative of the frozen configured moving-field kernel.

The retained moving_lim.py equations are reproduced here under explicit winding,
phase and leakage hypotheses.  This version fixes period-dependent opposite-face
registration and path resistance without changing archived reference results.
Current arises from voltage, resistance and field flux, not prescribed thrust.
It remains 2D prescribed-speed component research: no operating force map,
controller/converter qualification, finite-height returns or repeated duty pass.
"""
from copy import deepcopy
from pathlib import Path
from math import ceil, pi, sqrt, isfinite
from time import monotonic
from hashlib import sha256
import gzip, io, json, os, resource, subprocess, sys, tarfile, tempfile
import numpy as np
import scipy
from scipy.sparse import coo_matrix, csr_matrix, bmat, diags
from scipy.sparse.linalg import spsolve
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, digest, encoded
from engineering.design_search import wheel_motor, railway_bundle, transient_lim, lim_materials, lim_transport, lim_critical_mesh, capabilities

CODE='engineering/reference_cell/motor_refinement.py'
UPSTREAM='engineering/railway_completion/motor.py'
UPSTREAM_SHA256='da645b50f7f01eb16bcd8bd1247e88e5c73e09e2c437641ef954e4ad7d0f08de'
ANCESTOR='engineering/design_search/moving_lim.py'
ANCESTOR_SHA256='03a4d586fde84296fefd6f5c64c88f9c97373e1a27ef1b2aa6aea02202d81ae6'
REFERENCE='https://github.com/getdp-project/getdp/blob/master/templates/Lib_Magnetodynamics2D_av_Cir.pro'
SCOPE='Revised bounded numerical resources for identical configured moving-field equations and physical candidate: at most900s,512steps,3GiB,180000nodes; no changed physical limits, no operating acceptance'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
    manufacturing_release=False,operating_release=False,physical_journey_completed=False,native_evaluator_admission=False)


def _physical_revision(bundle,parameters,revision_reason):
    result=deepcopy(bundle);result['motor_parameters']=deepcopy(parameters)
    parameters=result['motor_parameters']
    definition=wheel_motor.definition(parameters);motor_id=definition['motor_component_id']
    result['motor_definition']=definition
    result['propulsion_component_id']=motor_id
    case=result['architecture_case'];old_case=case['case_id']
    physical=case['physical_definition']
    physical['propulsion_definition_id']=motor_id
    physical['wayside']['reference_motor_definition_id']=motor_id
    candidate_id=identity(physical)
    case.update(candidate_id=candidate_id,parent_case_ids=[old_case],generation=case['generation']+1)
    case['capability_composition']=capabilities.composition(result['family_id'],candidate_id,case['requirement_revision'])
    case['case_id']=identity({k:v for k,v in case.items() if k!='case_id'})
    result['physical_definition']['propulsion'].update(component_id=motor_id,
        physical_geometry=deepcopy(parameters['physical']),available_force_map=None)
    result.update(candidate_id=candidate_id,bundle_id=candidate_id,parent_bundle_id=bundle['bundle_id'],
        revision_reason=revision_reason,
        invalidated_evidence=['motor field/current/thermal','wayside mounts and clearances',
            'guideway station-equipment dead load','construction and whole-system economics'])
    brake=result['brake_definition']
    brake.update(candidate_id=candidate_id,propulsion_component_id=motor_id)
    brake['brake_definition_id']=identity({k:v for k,v in brake.items() if k!='brake_definition_id'})
    result['source_sha256'][CODE]=digest(__file__)
    result['definition_id']=identity({k:v for k,v in result.items() if k!='definition_id'})
    return railway_bundle.validate(result)



def variant(bundle,backiron_m):
    """Rewrite20m return steel while retaining its fixed passive interfaces."""
    railway_bundle.validate(bundle)
    if type(backiron_m) not in (int,float) or not isfinite(backiron_m) or not .025<=backiron_m<=.15:
        raise ValueError('Explicit20m backiron construction range .025.. .15m required')
    request(bundle,steps=1)
    original=bundle['motor_parameters']['physical']
    if original['periods']!=40 or original['primary_length_m']!=20.:
        raise ValueError('Backiron rewrites apply only to the separately identified20m/40period motor')
    if float(backiron_m)==original['backiron_m']:
        raise ValueError('A physical backiron rewrite must actually change the geometry')
    parameters=deepcopy(bundle['motor_parameters'])
    parameters['physical']['backiron_m']=float(backiron_m)
    parameters['physical']['name']='sparse-20m-backiron-'+str(float(backiron_m))
    reason='Bounded20m primary backiron rewrite from '+str(original['backiron_m'])+'m to '+str(float(backiron_m))+        'm; fixed passive fin/slot/winding/gap/formation; no operating force or selected-reference change'
    result=_physical_revision(bundle,parameters,reason)
    request(result,steps=1)
    return result


def rewound_variant(bundle):
    """Count larger conductor/slot stock, retaining the4A/mm2 RMS limit.

    Apparent electrical headroom is only a necessary ceiling, never thrust.
    Actual cooling, winding ends, insulation and installed converters remain open.
    """
    railway_bundle.validate(bundle);request(bundle,steps=1)
    p=bundle['motor_parameters']['physical']
    if p['periods']!=40 or p['primary_length_m']!=20.:
        raise ValueError('Rewinding applies only to the separately identified20m/40period motor')
    if p['slot_depth_m']==.08 and p['conductor_area_m2']==45e-6:
        raise ValueError('A physical rewinding must actually change the geometry')
    parameters=deepcopy(bundle['motor_parameters'])
    parameters['physical'].update(name='sparse-20m-rewound45mm2',backiron_m=.1,
        slot_depth_m=.08,conductor_area_m2=45e-6,turns_per_coil=40)
    parameters['evaluation'].update(current_peak_A=230.,wire_density_limit_RMS_A_mm2=4.)
    result=_physical_revision(bundle,parameters,
        'New20m winding:80mm slot,45mm2 conductor,40turns,100mm backiron;230A peak research envelope with unchanged4A/mm2 RMS limit; passive train unchanged')
    request(result,steps=1)
    return result



def wiring_definition(physical):
    periods,paths=physical['periods'],physical['parallel_paths_per_phase']
    if periods not in (25,40) or paths!=10 or 2*periods%paths:
        raise ValueError('Explicit25/40period and10path winding required')
    series=2*periods//paths
    value=dict(hypothesis='Round-robin face-period coil pairs; identical global signed-slot registration on both faces',
        branches=3*paths,parallel_paths_per_phase=paths,coils_per_path=series,coil_count=6*periods,
        opposite_face_coil_offset=periods,neutral='floating; total branch current zero',
        signed_slot_phase_indices=[0,2,1,0,2,1],signed_slot_signs=[1,-1,1,-1,1,-1],
        actual_connection_verified=False,actual_external_leakage_H=None,
        external_leakage_geometry_verified=False)
    value['wiring_hypothesis_id']=identity(value)
    return value


def request(bundle,*,start_m=5.5,speed_m_s=0.,voltage_peak_V=2.,frequency_Hz=30.,
            dt_s=.002,steps=4,mesh_m=.08,temperature_C=80.,current_limit_A=None,linear=False,
            transport_method='galerkin',mesh_family='legacy-tensor',critical_dx_m=None,secondary_dy_m=None,
            phase_direction=1,external_leakage_H=0.,maximum_nodes=180000,maximum_seconds=600.,memory_bytes=3*1024**3):
    railway_bundle.validate(bundle)
    if bundle['family_id']!='P1' or bundle.get('motor_parameters') is None:
        raise ValueError('Canonical passive P1 motor bundle required')
    parameters=bundle['motor_parameters'];definition=wheel_motor.definition(parameters)
    if definition!=bundle['motor_definition'] or definition['motor_component_id']!=bundle['propulsion_component_id']:
        raise ValueError('Canonical physical motor differs')
    p=definition['physical_configuration'];expected=wheel_motor.default_parameters()['physical']
    expected.update(primary_length_m=20. if p['periods']==40 else 12.5,periods=p['periods'])
    rewound=(p['periods']==40 and p['backiron_m']==.1 and p['slot_depth_m']==.08
             and p['conductor_area_m2']==45e-6 and p['turns_per_coil']==40)
    if rewound:
        expected.update(backiron_m=.1,slot_depth_m=.08,conductor_area_m2=45e-6)
    elif p['periods']==40 and .025<=p['backiron_m']<=.15:
        expected['backiron_m']=p['backiron_m']
    if {k:v for k,v in p.items() if k!='name'}!={k:v for k,v in expected.items() if k!='name'}:
        raise ValueError('Explicit retained25 or short-bank40 physical geometry required')
    wiring=wiring_definition(p)
    declared_cap=min(230. if rewound else 140.,parameters['evaluation']['current_peak_A'])
    density_limit=min(4.,parameters['evaluation']['wire_density_limit_RMS_A_mm2'])
    allowed_current=min(declared_cap,density_limit*sqrt(2)*p['conductor_area_m2']*1e6)
    if current_limit_A is None:current_limit_A=allowed_current
    values=(start_m,speed_m_s,voltage_peak_V,frequency_Hz,dt_s,mesh_m,current_limit_A,external_leakage_H,maximum_seconds)
    if any(type(v) not in (int,float) or not isfinite(v) for v in values):
        raise ValueError('Finite bounded component hypotheses required')
    if (abs(speed_m_s)>20 or not 0<=voltage_peak_V<=375 or not 1<=frequency_Hz<=100
        or not .00005<=dt_s<=.01 or not .005<=mesh_m<=.08 or not 0<current_limit_A<=allowed_current
        or not 0<=external_leakage_H<=.05 or not 0<maximum_seconds<=900.):
        raise ValueError('Electrical, time, leakage or mesh domain exceeded')
    if phase_direction not in (-1,1) or type(phase_direction) is not int:
        raise ValueError('Explicit travelling-wave phase direction required')
    if frequency_Hz*dt_s>=.5:
        raise ValueError('Nyquist sampling requires frequency_Hz*dt_s <0.5; not a convergence certificate')
    if (type(steps) is not int or not 1<=steps<=512 or temperature_C not in (20.,80.)
        or type(linear) is not bool or type(maximum_nodes) is not int or not 1<=maximum_nodes<=180000
        or type(memory_bytes) is not int or not 1024**3<=memory_bytes<=3*1024**3):
        raise ValueError('Explicit bounded time/material/resource contract required')
    finish=start_m+speed_m_s*dt_s*steps
    if min(start_m,finish)<-p['secondary_length_m']-.5 or max(start_m,finish)>p['primary_length_m']+.5:
        raise ValueError('Translation outside bounded entry/exit domain')
    r=dict(schema='osr-configured-moving-LIM-request/1',bundle_id=bundle['candidate_id'],
        bundle_definition_id=bundle['definition_id'],bundle_definition=deepcopy(bundle),
        body_candidate_id=bundle['body_candidate_id'],motor_component_id=definition['motor_component_id'],
        motor_definition=definition,physical_geometry=deepcopy(p),wiring=wiring,
        start_m=start_m,speed_m_s=speed_m_s,voltage_peak_V=voltage_peak_V,frequency_Hz=frequency_Hz,
        phase_direction=phase_direction,external_leakage_H_hypothesis=external_leakage_H,
        dt_s=dt_s,steps=steps,mesh_m=mesh_m,temperature_C=temperature_C,current_limit_A=current_limit_A,
        current_density_limit_RMS_A_mm2=density_limit,current_limit_basis_A=allowed_current,
        linear=linear,dc_bus_V_hypothesis=750.,transport_method=lim_transport.method(transport_method),
        mesh_family=mesh_family,maximum_nodes=maximum_nodes,maximum_seconds=maximum_seconds,memory_bytes=memory_bytes,
        actual_converter_loss_W=None,actual_cooling_W=None,repeated_thermal_duty_verified=False,
        available_operating_map=None,complete_installed_mass_kg=None,
        winding_connection_qualified=False,current_limiter_model='Abort at declared path-current envelope; not an implemented inverter current controller',
        phase_direction_scope='Reverses phase sequence, not a common180degree voltage negation; evaluation only',
        numerical_ancestry=dict(path=ANCESTOR,sha256=ANCESTOR_SHA256),
        references=[REFERENCE,lim_transport.REFERENCE],scope=SCOPE,**FLAGS)
    r['evaluated_component_definition_id']=identity(dict(motor_geometry_id=definition['motor_component_id'],wiring_hypothesis=wiring))
    if mesh_family==lim_critical_mesh.NAME:
        if mesh_m!=.04:
            raise ValueError('Critical mesh uses explicit targets; retain the legacy mesh mirror at .04m')
        r['mesh_definition']=lim_critical_mesh.definition(.02 if critical_dx_m is None else critical_dx_m,.00375 if secondary_dy_m is None else secondary_dy_m)
        lim_critical_mesh.axes(r)
    elif mesh_family!='legacy-tensor' or critical_dx_m is not None or secondary_dy_m is not None:
        raise ValueError('Supported mesh family and explicit variables required')
    r['request_id']=identity(r)
    return r


def validate(r):
    if not isinstance(r,dict) or not isinstance(r.get('bundle_definition'),dict):
        raise ValueError('Complete canonical component request required')
    keys=('start_m','speed_m_s','voltage_peak_V','frequency_Hz','dt_s','steps','mesh_m',
        'temperature_C','current_limit_A','linear','phase_direction','maximum_nodes','maximum_seconds','memory_bytes')
    if any(k not in r for k in keys):
        raise ValueError('Configured request fields missing')
    extra={}
    if r.get('mesh_family')==lim_critical_mesh.NAME:
        d=r.get('mesh_definition',{})
        if 'critical_dx_m' not in d or 'secondary_dy_m' not in d:
            raise ValueError('Explicit critical mesh targets required')
        extra=dict(critical_dx_m=d['critical_dx_m'],secondary_dy_m=d['secondary_dy_m'])
    expected=request(r['bundle_definition'],**{k:r[k] for k in keys},
        external_leakage_H=r.get('external_leakage_H_hypothesis'),
        transport_method=r.get('transport_method',{}).get('name'),mesh_family=r.get('mesh_family'),**extra)
    if r!=expected:
        raise ValueError('Configured request differs from canonical geometry, winding, resource or evaluation constructor')
    return r


def phase_commands(r,time):
    return np.repeat(r['voltage_peak_V']*np.cos(2*pi*r['frequency_Hz']*time-r['phase_direction']*np.arange(3)*2*pi/3),
                     r['physical_geometry']['parallel_paths_per_phase'])


def path_resistance(r):
    p,d=r['physical_geometry'],r['motor_definition']
    rho=d['copper_resistivity_20C_ohm_m_hypothesis']*(1+d['copper_temperature_coefficient_K_inv_hypothesis']*(r['temperature_C']-20))
    return np.full(r['wiring']['branches'],r['wiring']['coils_per_path']*rho*d['wire_length_m_per_coil']/p['conductor_area_m2'])


def _subdivide(edges,h):
    edges=sorted(set(round(float(x),12) for x in edges));out=[]
    for a,b in zip(edges,edges[1:]):out.extend(np.linspace(a,b,max(1,ceil((b-a)/h))+1)[:-1])
    return np.r_[out,edges[-1]]


def _mesh_axes(r):
    if r.get('mesh_family')==lim_critical_mesh.NAME:return lim_critical_mesh.axes(r)
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
    if r.get('mesh_family')==lim_critical_mesh.NAME:result['active_grid']=lim_critical_mesh.diagnostics(r,x,y)
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
            rows=inside&(centers[:,1]*side>0);period=k//6;coil_index=(0 if side<0 else p['periods'])+period
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
    area,grad=transient_lim.geometry(points,tri);N=len(points);free=np.setdiff1d(np.arange(N),boundary);nf=len(free);nc=r['wiring']['branches']
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
    R=path_resistance(r);leakage=r['external_leakage_H_hypothesis']
    A=np.zeros(N);I=np.zeros(nc);u=neutral=0.;rows=[];last_energy=0.;curve=lim_materials.material();state='completed'
    for step in range(1,r['steps']+1):
        if monotonic()-started>r['maximum_seconds']:raise TimeoutError('Moving component numerical time budget exceeded')
        old=A.copy();oldI=I.copy();time=step*dt;start=r['start_m']+v*time
        m0,m1,m2=conductor_moments(points,tri,area,start,p['secondary_length_m'],p['secondary_thickness_m'])
        if abs(m0.sum()-p['secondary_length_m']*p['secondary_thickness_m'])>1e-9:raise ValueError('Moving conductor volume lost or duplicated')
        M=matrix(sigma*m2);C=matrix(sigma*v*m1[:,:,None]*grad[:,None,:,0]);b=np.bincount(tri.ravel(),weights=(sigma*m1).ravel(),minlength=N);closure=np.asarray(C.sum(axis=0)).ravel();S=sigma*m0.sum()
        stabilization=lim_transport.operators(m0,m1,grad[:,:,0],sigma=sigma,speed=v,diffusivity=1/(transient_lim.MU0*sigma),name=r['transport_method']['name'])
        Ms=matrix(stabilization['mass']);Cs=matrix(stabilization['transport']);bs=np.bincount(tri.ravel(),weights=stabilization['floating'].ravel(),minlength=N)
        command=phase_commands(r,time)
        for iteration in range(24):
            local,jac,ga,B,nu,energy_density=transient_lim.magnetic(A,tri,area,grad,regions,curve,r['linear'])
            At=(A-old)/dt;fa=np.bincount(tri.ravel(),weights=local.ravel(),minlength=N)+(M+Ms)@At+(C+Cs)@A+(b+bs)*u-W@I
            residual=np.r_[fa[free],b@At+closure@A+S*u,R*I+leakage*(I-oldI)/dt+h*(W.T@At)+neutral-command,I.sum()]
            norm=float(np.linalg.norm(residual))
            if norm<1e-8*max(1.,np.linalg.norm(command)):break
            K=matrix(jac)+(M+Ms)/dt+C+Cs
            J=circuit_jacobian(K[free][:,free],b[free],closure[free],S,Wf,R+leakage/dt,dt,h,field_b=(b+bs)[free])
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
        leakage_work=float(leakage*np.dot(I,I-oldI)/dt)
        leakage_energy=float(.5*leakage*np.dot(I,I))
        leakage_dissipation=float(.5*leakage*np.dot(I-oldI,I-oldI)/dt)
        stabilization_W=lim_transport.power(At[tri],A[tri],u,stabilization,h)
        residual_W=terminal-copper-heat-float(v*force[0])-field_work-stabilization_W-leakage_work
        row=dict(time_s=time,secondary_start_m=start,secondary_end_m=start+p['secondary_length_m'],
            overlap_primary_m=max(0.,min(start+p['secondary_length_m'],p['primary_length_m'])-max(0.,start)),
            conductor_area_m2=float(m0.sum()),conductor_first_moment_x_m3=float(sum(np.einsum('ti,ti->t',m1,points[tri][:,:,0]))),
            path_currents_A=I.tolist(),phase_currents_A=I.reshape(3,p['parallel_paths_per_phase']).sum(axis=1).tolist(),
            path_flux_linkage_Wb_turn=(h*(W.T@A)+leakage*I).tolist(),
            phase_voltage_commands_V=command[::p['parallel_paths_per_phase']].tolist(),neutral_voltage_V=float(neutral),
            terminal_W=terminal,primary_copper_W=copper,secondary_Joule_W=heat,thrust_N=float(force[0]),normal_force_N=float(force[1]),
            mechanical_W=float(v*force[0]),magnetic_energy_J=stored,backward_Euler_dissipation_W=float(algorithmic),
            external_leakage_energy_J=leakage_energy,external_leakage_BE_dissipation_W=leakage_dissipation,
            external_leakage_work_W=leakage_work,stabilization_work_W=stabilization_W,stabilization_work_is_physical_heat=False,
            discrete_power_residual_W=float(residual_W),net_secondary_current_A=net_secondary_current(sigma,m1,D),
            net_terminal_current_A=float(I.sum()),peak_steel_B_T=float(max(B[regions==3])),coupled_residual=norm,Newton_iterations=iteration)
        rows.append(row)
        if progress:progress(row)
        last_energy=stored
        if max(abs(I))>r['current_limit_A']:state='current-limit';break
        if r['linear'] and row['peak_steel_B_T']>1.3:state='outside-linear-steel-domain';break
    return dict(execution='completed',state=state,trace=rows,nodes=N,elements=len(tri),Peclet_max=pe,mesh_diagnostics=bounds.get('active_grid'),actual_mesh=actual_mesh,
        final_A_sha256=identity(A.tolist()),final_current_A=I.tolist(),
        moving_geometry_simulated=True,current_circuit_coupled=True,wire_resistance_ohm_per_path=R.tolist(),external_leakage_H_hypothesis=leakage,
        phase_direction=r['phase_direction'],flux_linkage_evaluated=True,converter_current_control_verified=False,transport_method=r['transport_method'],
        available_operating_map=None,actual_converter_loss_W=None,temperature_C_prediction=None,
        repeated_thermal_duty_verified=False,finite_height_return_current_verified=False,
        installed_force_available_N=None,numerical_validity='algebraic-residuals-evaluated-spatial-time-convergence-unconfirmed',
        engineering_screen='unknown' if state=='completed' else 'failed-declared-component-screen',**FLAGS)


def sources(root=ROOT):
    names=(CODE,UPSTREAM,ANCESTOR,lim_critical_mesh.CODE,lim_transport.CODE,wheel_motor.PRODUCER,
        transient_lim.PRODUCER,'engineering/design_search/lim_materials.py',lim_materials.DATA,
        'engineering/design_search/railway_bundle.py','engineering/design_search/capabilities.py','engineering/station_rail/common.py',
        'engineering/station_rail/station_motor.py','engineering/requirements.txt')
    result={name:digest(Path(root)/name) for name in names}
    if result[UPSTREAM]!=UPSTREAM_SHA256:
        raise ValueError('Frozen configured-kernel ancestor changed; new independent comparison required')
    if result[ANCESTOR]!=ANCESTOR_SHA256:
        raise ValueError('Retained numerical ancestor changed; independent reference comparison required')
    return result


def _tool(r):
    import scipy.sparse.linalg._dsolve._superlu as superlu
    return dict(python=sys.version,python_sha256=digest(sys.executable),numpy=np.__version__,
        scipy=scipy.__version__,superlu_sha256=digest(superlu.__file__),
        OPENBLAS_NUM_THREADS=os.environ.get('OPENBLAS_NUM_THREADS'),OMP_NUM_THREADS=os.environ.get('OMP_NUM_THREADS'),
        enforced_address_space_limit_bytes=resource.getrlimit(resource.RLIMIT_AS)[0],
        requested_address_space_limit_bytes=r['memory_bytes'])


TOOL_IDENTITY_FIELDS=('python','python_sha256','numpy','scipy','superlu_sha256')


def _recorded_tool(tool,r):
    """Check a recorded worker contract, independently of the reader's tools."""
    required=set(TOOL_IDENTITY_FIELDS)|{'OPENBLAS_NUM_THREADS','OMP_NUM_THREADS',
        'enforced_address_space_limit_bytes','requested_address_space_limit_bytes'}
    if not isinstance(tool,dict) or set(tool)!=required:
        raise ValueError('Recorded numerical tool schema differs')
    if any(not isinstance(tool[k],str) or not tool[k].strip() for k in TOOL_IDENTITY_FIELDS):
        raise ValueError('Recorded numerical tool identity missing')
    for key in ('python_sha256','superlu_sha256'):
        value=tool[key]
        if len(value)!=64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('Recorded numerical tool digest differs')
    if (type(tool['enforced_address_space_limit_bytes']) is not int
        or type(tool['requested_address_space_limit_bytes']) is not int
        or tool['enforced_address_space_limit_bytes']!=r['memory_bytes']
        or tool['requested_address_space_limit_bytes']!=r['memory_bytes']
        or tool['OPENBLAS_NUM_THREADS']!='1' or tool['OMP_NUM_THREADS']!='1'):
        raise ValueError('Executed worker resource/thread contract differs')
    return {key:tool[key] for key in TOOL_IDENTITY_FIELDS}


def _input_sources(root,source):
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w') as archive:
        total=0
        for name,expected in sorted(source.items()):
            path=Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Ordinary numerical source paths required')
            p=Path(root)/path
            if p.is_symlink():raise ValueError('Linked numerical source refused')
            raw=p.read_bytes();total+=len(raw)
            if sha256(raw).hexdigest()!=expected or total>32*1024**2:
                raise ValueError('Numerical source bytes or package bound differ')
            item=tarfile.TarInfo(name);item.size=len(raw);item.mtime=0;item.mode=0o644
            archive.addfile(item,io.BytesIO(raw))
    return gzip.compress(buffer.getvalue(),mtime=0)


def _decorate(worker,r,source):
    result=deepcopy(worker)
    result.update(request_id=r['request_id'],bundle_id=r['bundle_id'],
        body_candidate_id=r['body_candidate_id'],motor_component_id=r['motor_component_id'],
        evaluated_component_definition_id=r['evaluated_component_definition_id'],
        source_sha256=source,scope=SCOPE,evidence_kind='configured-moving-component-method',
        canonical_interface_qualification='held-unverified-wiring-3D-converter-and-thermal',
        operating_map_admitted=False)
    result['evaluation_id']=identity(result)
    return result


def run(r,output,*,root=ROOT):
    """Execute one bounded worker; all failures and partial traces are retained."""
    validate(r);root=Path(root).resolve();out=Path(output).resolve()
    if out.exists():raise ValueError('Fresh immutable component run directory required')
    source=sources(root)
    if source[CODE]!=digest(__file__):raise ValueError('Executing configured kernel differs from source tree')
    out.mkdir(parents=True)
    (out/'input.json').write_bytes(encoded(dict(request=r,source_sha256=source)))
    (out/'input-sources.tar.gz').write_bytes(_input_sources(root,source))
    preflight=estimate(r)
    (out/'preflight.json').write_bytes(encoded(preflight))
    timeout=r['maximum_seconds']+5.
    if not preflight['mesh_nodes_within_budget'] or (not preflight['unstabilized_domain_supported'] and r['transport_method']['name']=='galerkin'):
        reason='Necessary mesh-node bound exceeded' if not preflight['mesh_nodes_within_budget'] else 'Unstabilized conductor Peclet>1'
        worker=dict(execution='held-preflight',reason=reason,trace=[],**FLAGS)
        (out/'stdout.log').write_bytes(b'');(out/'stderr.log').write_bytes(b'')
    else:
        def limit():resource.setrlimit(resource.RLIMIT_AS,(r['memory_bytes'],r['memory_bytes']))
        try:
            proc=subprocess.run([sys.executable,'-m','engineering.reference_cell.motor_refinement','--worker',str(out)],
                cwd=root,capture_output=True,timeout=timeout,preexec_fn=limit,
                env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
            (out/'stdout.log').write_bytes(proc.stdout);(out/'stderr.log').write_bytes(proc.stderr)
            worker=json.loads((out/'worker-result.json').read_bytes()) if (out/'worker-result.json').is_file() else dict(
                execution='tool-error',reason='Worker returned '+str(proc.returncode),trace=[],**FLAGS)
        except subprocess.TimeoutExpired as error:
            (out/'stdout.log').write_bytes(error.stdout or b'');(out/'stderr.log').write_bytes(error.stderr or b'')
            worker=dict(execution='interrupted',reason='Bounded worker deadline exceeded; partial trace retained',trace=[],**FLAGS)
    if sources(root)!=source:raise ValueError('Configured kernel source changed; unsealed inputs/logs retained')
    result=_decorate(worker,r,source)
    (out/'result.json').write_bytes(encoded(result))
    manifest=dict(schema='osr-configured-moving-LIM-package/1',evaluation_id=result['evaluation_id'],
        source_sha256=source,files_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},**FLAGS)
    manifest['manifest_id']=identity(manifest)
    (out/'manifest.json').write_bytes(encoded(manifest))
    return result


def _trace_check(r,result):
    if (result.get('available_operating_map') is not None or result.get('installed_force_available_N') is not None
        or result.get('repeated_thermal_duty_verified',False) is not False
        or result.get('converter_current_control_verified',False) is not False):
        raise ValueError('Component response cannot become installed propulsion or operating evidence')
    if result.get('execution')!='completed':return
    rows=result.get('trace',[])
    if not 1<=len(rows)<=r['steps']:
        raise ValueError('Executed component trace coverage differs')
    R=path_resistance(r);old_energy=0.;oldI=np.zeros(len(R));dt=r['dt_s'];L=r['external_leakage_H_hypothesis']
    for index,row in enumerate(rows,1):
        current=np.asarray(row['path_currents_A'],dtype=float)
        if current.shape!=R.shape or not np.isfinite(current).all():
            raise ValueError('Finite complete path-current vector required')
        time=index*dt;start=r['start_m']+r['speed_m_s']*time;p=r['physical_geometry']
        values=dict(time_s=time,secondary_start_m=start,secondary_end_m=start+p['secondary_length_m'],
            conductor_area_m2=p['secondary_length_m']*p['secondary_thickness_m'],
            conductor_first_moment_x_m3=p['secondary_length_m']*p['secondary_thickness_m']*(start+p['secondary_length_m']/2),
            primary_copper_W=float(np.dot(R,current*current)),net_terminal_current_A=float(current.sum()),
            external_leakage_energy_J=float(.5*L*np.dot(current,current)),
            external_leakage_work_W=float(L*np.dot(current,current-oldI)/dt),
            external_leakage_BE_dissipation_W=float(.5*L*np.dot(current-oldI,current-oldI)/dt),
            mechanical_W=r['speed_m_s']*row['thrust_N'])
        for key,value in values.items():
            actual=row.get(key)
            if type(actual) not in (int,float) or not isfinite(actual) or abs(actual-value)>1e-7*max(1.,abs(value)):
                raise ValueError('Component trace arithmetic/geometry differs: '+key)
        phase=current.reshape(3,p['parallel_paths_per_phase']).sum(axis=1)
        command=phase_commands(r,time)[::p['parallel_paths_per_phase']]
        if not np.allclose(row['phase_currents_A'],phase,rtol=1e-9,atol=1e-9) or not np.allclose(row['phase_voltage_commands_V'],command,rtol=1e-9,atol=1e-9):
            raise ValueError('Phase registration/current aggregation differs')
        field_work=(row['magnetic_energy_J']-old_energy)/dt+row['backward_Euler_dissipation_W']
        residual=row['terminal_W']-row['primary_copper_W']-row['secondary_Joule_W']-row['mechanical_W']-field_work-row['stabilization_work_W']-row['external_leakage_work_W']
        if abs(row['discrete_power_residual_W']-residual)>1e-6*max(1.,abs(row['terminal_W'])):
            raise ValueError('Discrete power balance receipt differs')
        old_energy=row['magnetic_energy_J'];oldI=current


def verify(output,*,root=ROOT,replay=False,require_current_tool=True):
    """Verify recorded evidence, or require the exact current tool for reuse.

    Recorded mode validates payload/source/trace and the saved worker contract.
    It does not claim that the reader has the generating numerical toolchain.
    Exact replay always requires matching tools, regardless of recorded mode.
    """
    if type(require_current_tool) is not bool or type(replay) is not bool:
        raise ValueError('Explicit boolean tool/replay policy required')
    out=Path(output);root=Path(root)
    if out.is_symlink() or any(p.is_symlink() for p in out.iterdir()):raise ValueError('Ordinary numerical package required')
    manifest=json.loads((out/'manifest.json').read_bytes());result=json.loads((out/'result.json').read_bytes())
    data=json.loads((out/'input.json').read_bytes());r=validate(data['request']);source=sources(root)
    if (manifest.get('schema')!='osr-configured-moving-LIM-package/1'
        or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
        or manifest.get('evaluation_id')!=result.get('evaluation_id')
        or result.get('evaluation_id')!=identity({k:v for k,v in result.items() if k!='evaluation_id'})
        or manifest.get('source_sha256')!=source or data.get('source_sha256')!=source
        or result.get('source_sha256')!=source
        or manifest.get('files_sha256')!={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}
        or gzip.decompress((out/'input-sources.tar.gz').read_bytes())!=gzip.decompress(_input_sources(root,source))
        or json.loads((out/'preflight.json').read_bytes())!=estimate(r)
        or any(manifest.get(k) is not v or result.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('Configured component source, payload, identity or disposition differs')
    worker=json.loads((out/'worker-result.json').read_bytes()) if (out/'worker-result.json').is_file() else {
        k:v for k,v in result.items() if k not in ('request_id','bundle_id','body_candidate_id','motor_component_id',
            'evaluated_component_definition_id','source_sha256','scope','evidence_kind','canonical_interface_qualification','operating_map_admitted','evaluation_id')}
    if _decorate(worker,r,source)!=result:
        raise ValueError('Worker record and result candidate/evaluation differ')
    _trace_check(r,result)
    actual=_tool(r)
    current_tool_identity={key:actual[key] for key in TOOL_IDENTITY_FIELDS}
    recorded_tool_identity=None
    if 'tool' in result or result.get('execution')=='completed':
        recorded_tool_identity=_recorded_tool(result.get('tool'),r)
    toolchain_matches_current=recorded_tool_identity is not None and recorded_tool_identity==current_tool_identity
    if recorded_tool_identity is not None and (require_current_tool or replay) and not toolchain_matches_current:
        raise ValueError('Numerical tool identity differs; recorded integrity is not exact native reuse or replay')
    if replay and recorded_tool_identity is None and result.get('execution')!='held-preflight':
        raise ValueError('Exact replay requires a recorded numerical tool identity')
    replay_output=None;replay_completed=False
    if replay:
        # An independent replay receives the same actual subprocess/RAM/thread
        # budget. Never run a potentially large field solve in the verifier.
        replay_output=Path(tempfile.mkdtemp(prefix='configured-motor-replay-',dir=out.parent))/'execution'
        reproduced=run(r,replay_output,root=root)
        if reproduced!=result:
            raise ValueError('Independent configured component replay differs; retained at '+str(replay_output))
        replay_completed=reproduced.get('execution')=='completed'
    return dict(verified=True,evaluation_id=result['evaluation_id'],request_id=r['request_id'],
        execution=result['execution'],independent_execution_attempted=replay,
        numerical_replay_executed=replay_completed,replay_package=None if replay_output is None else str(replay_output),
        recorded_tool_identity=recorded_tool_identity,current_tool_identity=current_tool_identity,
        toolchain_matches_current=toolchain_matches_current,
        native_reuse_eligible=bool(toolchain_matches_current and result.get('execution')=='completed'),
        require_current_tool=require_current_tool,
        verification_scope=('Exact current-tool identity and source/payload/trace checks' if require_current_tool else
            'Recorded-tool archive integrity and source/payload/trace checks; current-tool use is not asserted')+
            '; spatial-time convergence and physical correlation remain separate',**FLAGS)


def _worker(folder):
    out=Path(folder);data=json.loads((out/'input.json').read_bytes());r=data['request']
    try:
        if sources()!=data['source_sha256']:raise ValueError('Configured worker source differs')
        def progress(row):
            with (out/'partial-trace.jsonl').open('a') as stream:
                stream.write(json.dumps(row,sort_keys=True)+'\n')
        result=solve(r,progress=progress)
    except Exception as error:
        result=dict(execution='interrupted' if isinstance(error,TimeoutError) else 'held',
            reason=type(error).__name__+': '+str(error),trace=[],**FLAGS)
    result['tool']=_tool(r)
    (out/'worker-result.json').write_bytes(encoded(result))


def compare(packages,*,root=ROOT):
    """Compare two completed, same-horizon time refinements without qualifying them."""
    if len(packages)!=2:raise ValueError('Exactly two independently retained refinement packages required')
    values=[]
    for folder in packages:
        verified=verify(folder,root=root)
        r=json.loads((Path(folder)/'input.json').read_bytes())['request']
        result=json.loads((Path(folder)/'result.json').read_bytes())
        values.append((r,result,verified))
    values.sort(key=lambda x:-x[0]['dt_s'])
    coarse,fine=values
    drop={'dt_s','steps','maximum_seconds','request_id'}
    common=lambda r:{k:v for k,v in r.items() if k not in drop}
    if common(coarse[0])!=common(fine[0]) or not coarse[0]['dt_s']>fine[0]['dt_s']:
        raise ValueError('Time refinement must retain exact physical, mesh, source, current and frequency inputs')
    horizon=coarse[0]['dt_s']*coarse[0]['steps']
    if abs(horizon-fine[0]['dt_s']*fine[0]['steps'])>1e-12:
        raise ValueError('Time refinements require exactly matched requested horizons')
    completed=all(v[1].get('execution')=='completed' and v[1].get('state')=='completed' and len(v[1].get('trace',[]))==v[0]['steps'] for v in values)
    result=dict(schema='osr-moving-LIM-time-refinement/1',candidate_id=coarse[0]['bundle_id'],
        motor_component_id=coarse[0]['motor_component_id'],requested_horizon_s=horizon,
        evaluations=[x[1]['evaluation_id'] for x in values],completed_same_horizon=completed,
        time_steps_s=[x[0]['dt_s'] for x in values],matched_points=0,
        relative_thrust_RMS_change=None,relative_current_RMS_change=None,
        last_thrust_N=None,tail_mean_thrust_N=None,approved_convergence_limit=None,
        numerical_time_convergence='unconfirmed',spatial_convergence='unconfirmed',
        available_operating_map=None,physical_correlation='missing',source_sha256=sources(root),**FLAGS)
    if completed:
        if coarse[1]['actual_mesh']!=fine[1]['actual_mesh']:
            raise ValueError('Time refinement changed actual mesh')
        rows={round(r['time_s'],12):r for r in fine[1]['trace']}
        pairs=[(r,rows[round(r['time_s'],12)]) for r in coarse[1]['trace'] if round(r['time_s'],12) in rows]
        if len(pairs)!=len(coarse[1]['trace']):raise ValueError('Fine trace does not cover every coarse time')
        def relative(a,b):
            aa=np.asarray(a);bb=np.asarray(b);return float(np.linalg.norm(aa-bb)/max(1e-12,np.linalg.norm(bb)))
        result.update(matched_points=len(pairs),
            relative_thrust_RMS_change=relative([a['thrust_N'] for a,b in pairs],[b['thrust_N'] for a,b in pairs]),
            relative_current_RMS_change=relative([a['path_currents_A'] for a,b in pairs],[b['path_currents_A'] for a,b in pairs]),
            last_thrust_N=[v[1]['trace'][-1]['thrust_N'] for v in values],
            tail_mean_thrust_N=[float(np.mean([r['thrust_N'] for r in v[1]['trace'] if r['time_s']>horizon-2/v[0]['frequency_Hz']-1e-12])) for v in values])
    result['evaluation_id']=identity(result)
    return result


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='--worker':
        raise SystemExit('Internal bounded worker; use motor.request/run/verify')
    _worker(sys.argv[2])


