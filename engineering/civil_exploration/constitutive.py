"""Region-specific constitutive, laminate, interface and fatigue evaluations.

Strengths, curves, lengths and limits are supplied inputs. Equations can be
verified synthetically; no input is promoted to a measured material property.
"""
from __future__ import annotations
import math
from numbers import Real
import numpy as np
from scipy.optimize import least_squares
from .materials import fatigue_damage, prestress


def value(x,name,positive=False):
    if isinstance(x,bool) or not isinstance(x,Real) or not math.isfinite(x) or (positive and x<=0):raise ValueError('invalid constitutive '+name)
    return float(x)


def interpolate(points,x):
    array=np.asarray(points,dtype=float)
    if array.ndim!=2 or array.shape[1]!=2 or len(array)<2 or not np.isfinite(array).all() or np.any(np.diff(array[:,0])<=0):
        raise ValueError('ordered finite material curve required')
    if not array[0,0]<=x<=array[-1,0]:raise ValueError('material interpolation outside supplied validity range')
    return float(np.interp(x,array[:,0],array[:,1]))


def concrete_state(record,age_days,temperature_c):
    age=value(age_days,'age',True);temperature=value(temperature_c,'temperature')
    E=interpolate(record['age_modulus_pa'],age)*interpolate(record['temperature_modulus_factor'],temperature)
    fc=interpolate(record['age_strength_pa'],age)*interpolate(record['temperature_strength_factor'],temperature)
    phi=interpolate(record['creep_coefficient'],age);shrink=interpolate(record['shrinkage_strain'],age)
    if E<=0 or fc<=0 or phi<0:raise ValueError('nonpositive material stiffness/strength or negative creep')
    return dict(E_pa=E/(1+phi),instantaneous_E_pa=E,fc_pa=fc,
        ft_pa=value(record['ft_pa'],'tension strength',True),eps_c0=value(record['eps_c0'],'peak strain',True)*(1+phi),
        eps_cu=value(record['eps_cu'],'ultimate strain',True)*(1+phi),fracture_energy_n_m=value(record['fracture_energy_n_m'],'fracture energy',True),
        eigenstrain=shrink+record['thermal_expansion_per_c']*(temperature-record['reference_temperature_c']),
        creep_coefficient=phi,age_days=age,temperature_c=temperature)


def concrete_stress(strain,state,characteristic_length_m):
    eps=value(strain,'strain')-state['eigenstrain'];E=state['E_pa'];length=value(characteristic_length_m,'crack band length',True)
    if state['eps_cu']<=state['eps_c0']:raise ValueError('concrete ultimate strain must follow its peak')
    if eps<0:
        x=-eps/state['eps_c0']
        ratio=E*state['eps_c0']/state['fc_pa']
        if not 0<ratio<=3:raise ValueError('concrete modulus/peak strain needs a compatible monotone cubic law')
        if x<=1:return -state['fc_pa']*(ratio*x+(3-2*ratio)*x*x+(ratio-2)*x**3),False
        if -eps<state['eps_cu']:return -state['fc_pa']*(state['eps_cu']+eps)/(state['eps_cu']-state['eps_c0']),False
        return 0.,True
    cracking=state['ft_pa']/E
    if eps<=cracking:return E*eps,False
    opening=(eps-cracking)*length
    return state['ft_pa']*math.exp(-state['ft_pa']*opening/state['fracture_energy_n_m']),False


def steel_return(strain,record,previous=None):
    E=value(record['E_pa'],'steel modulus',True);fy=value(record['yield_pa'],'yield',True)
    H=value(record['hardening_pa'],'hardening');state=previous or dict(plastic_strain=0.,equivalent_plastic_strain=0.)
    if H<0:raise ValueError('negative steel hardening is not supported')
    trial=E*(value(strain,'steel strain')-state['plastic_strain']);limit=fy+H*state['equivalent_plastic_strain']
    increment=max(0.,abs(trial)-limit)/(E+H);sign=math.copysign(1.,trial)
    stress=trial-sign*E*increment
    return dict(stress_pa=stress,plastic_strain=state['plastic_strain']+sign*increment,
                equivalent_plastic_strain=state['equivalent_plastic_strain']+increment,
                plastic_dissipation_j_m3=limit*increment,engineering_released=False)


def laminate(plies):
    if not plies:raise ValueError('explicit composite plies required')
    height=sum(value(p['thickness_m'],'ply thickness',True) for p in plies);z=-height/2
    A=np.zeros((3,3));B=np.zeros((3,3));D=np.zeros((3,3));layers=[]
    for p in plies:
        E1=value(p['E1_pa'],'ply E1',True);E2=value(p['E2_pa'],'ply E2',True);G=value(p['G12_pa'],'ply G12',True)
        nu=value(p['nu12'],'ply Poisson ratio');nu21=nu*E2/E1
        if 1-nu*nu21<=0:raise ValueError('nonpositive ply compliance')
        q11=E1/(1-nu*nu21);q22=E2/(1-nu*nu21);q12=nu*E2/(1-nu*nu21)
        m=math.cos(math.radians(p['angle_deg']));n=math.sin(math.radians(p['angle_deg']))
        qbar=np.array([
            [q11*m**4+2*(q12+2*G)*m*m*n*n+q22*n**4,(q11+q22-4*G)*m*m*n*n+q12*(m**4+n**4),(q11-q12-2*G)*m**3*n-(q22-q12-2*G)*m*n**3],
            [0.,q11*n**4+2*(q12+2*G)*m*m*n*n+q22*m**4,(q11-q12-2*G)*m*n**3-(q22-q12-2*G)*m**3*n],
            [0.,0.,(q11+q22-2*q12-2*G)*m*m*n*n+G*(m**4+n**4)]])
        qbar[1,0]=qbar[0,1];qbar[2,0]=qbar[0,2];qbar[2,1]=qbar[1,2]
        top=z+p['thickness_m'];A+=qbar*(top-z);B+=qbar*(top*top-z*z)/2;D+=qbar*(top**3-z**3)/3
        layers.append(dict(z_bottom_m=z,z_top_m=top,Qbar_pa=qbar.tolist(),material=p));z=top
    ABD=np.block([[A,B],[B,D]])
    if np.linalg.eigvalsh(ABD).min()<=0:raise ValueError('laminate lacks positive strain energy')
    return dict(A_n_m=A.tolist(),B_n=B.tolist(),D_nm=D.tolist(),ABD=ABD.tolist(),layers=layers,total_thickness_m=height,
                longitudinal_modulus_pa=1/(np.linalg.inv(ABD)[0,0]*height),physical_validation=False)


def ply_failure(stress_local,record):
    s1,s2,tau=np.asarray(stress_local,dtype=float)
    keys=('Xt_pa','Xc_pa','Yt_pa','Yc_pa','S_pa')
    if any(record.get(k) is None for k in keys):return dict(failure_index=None,strength_evidence_complete=False)
    Xt,Xc,Yt,Yc,S=[value(record[k],k,True) for k in keys]
    # Maximum stress does not invent the unmeasured Tsai-Wu interaction term.
    ratio=max(abs(s1)/(Xt if s1>=0 else Xc),abs(s2)/(Yt if s2>=0 else Yc),abs(tau)/S)
    return dict(failure_index=float(ratio),strength_evidence_complete=True,criterion='maximum local ply stress',engineering_released=False)


def laminate_response(plies,axial_strain):
    properties=laminate(plies);unit=np.linalg.solve(np.asarray(properties['ABD']),[1.,0.,0.,0.,0.,0.])
    state=unit*(axial_strain/unit[0]);rows=[]
    for layer in properties['layers']:
        p=layer['material'];theta=math.radians(p['angle_deg']);m=math.cos(theta);n=math.sin(theta)
        nu=p['nu12'];denom=1-nu*nu*p['E2_pa']/p['E1_pa']
        Q=np.asarray([[p['E1_pa']/denom,nu*p['E2_pa']/denom,0.],
                      [nu*p['E2_pa']/denom,p['E2_pa']/denom,0.],[0.,0.,p['G12_pa']]])
        for z in (layer['z_bottom_m'],layer['z_top_m']):
            ex,ey,gamma=state[:3]+z*state[3:]
            local=np.asarray([m*m*ex+n*n*ey+m*n*gamma,n*n*ex+m*m*ey-m*n*gamma,
                              -2*m*n*ex+2*m*n*ey+(m*m-n*n)*gamma])
            stress=Q@local;rows.append(dict(z_m=z,stress_local_pa=stress.tolist(),**ply_failure(stress,p)))
    return dict(stress_pa=properties['longitudinal_modulus_pa']*axial_strain,
                generalised_strains=state.tolist(),ply_faces=rows,physical_validation=False)


def cohesive(displacement,record,previous_damage=0.):
    d=np.asarray(displacement,dtype=float)
    if d.shape!=(3,) or not np.isfinite(d).all():raise ValueError('finite normal/two-shear interface opening required')
    Kn=value(record['normal_stiffness_n_m3'],'normal interface stiffness',True);Ks=value(record['shear_stiffness_n_m3'],'shear interface stiffness',True)
    tn=value(record['normal_strength_pa'],'normal interface strength',True);ts=value(record['shear_strength_pa'],'shear interface strength',True)
    Gn=value(record['mode_I_energy_n_m'],'mode I energy',True);Gs=value(record['mode_II_energy_n_m'],'mode II energy',True)
    opening=max(d[0],0.);shear=float(np.linalg.norm(d[1:]));effective=math.hypot(opening,shear)
    if not 0<=previous_damage<=1:raise ValueError('interface damage outside [0,1]')
    mode_fraction=Ks*shear*shear/(Kn*opening*opening+Ks*shear*shear) if effective else 0.
    Gc=Gn+(Gs-Gn)*mode_fraction**value(record['bk_exponent'],'mixed mode exponent',True)
    direction=np.array([opening,shear])/effective if effective else np.array([1.,0.])
    initial=1/math.sqrt((Kn*direction[0]/tn)**2+(Ks*direction[1]/ts)**2)
    initial_traction=initial*(Kn*direction[0]**2+Ks*direction[1]**2);ultimate=2*Gc/initial_traction
    if ultimate<=initial:raise ValueError('interface energy is below its elastic initiation energy')
    damage=0. if effective<=initial else min(1.,ultimate*(effective-initial)/(effective*(ultimate-initial)))
    damage=max(float(previous_damage),damage)
    traction=np.asarray([(Kn*d[0] if d[0]<0 else (1-damage)*Kn*d[0]),*(1-damage)*Ks*d[1:]])
    return dict(traction_pa=traction.tolist(),damage=damage,fracture_energy_n_m=Gc,
                complete_debonding=damage>=1,compressive_contact_retained=d[0]<0,physical_validation=False)


def section_response(section,materials,demand,age_days=28.,temperature_c=20.,fibers_per_region=6,characteristic_length_m=.5):
    if type(fibers_per_region) is not int or not 2<=fibers_per_region<=32:raise ValueError('bounded section fiber discretisation required')
    roles=section.get('material_roles',['concrete']*len(section['regions']));fibers=[]
    if len(roles)!=len(section['regions']):raise ValueError('every section region requires one material role')
    for region,role in zip(section['regions'],roles):
        if role not in materials:raise ValueError('assembled section lacks material law: '+role)
        law=materials[role]
        for i in range(fibers_per_region):
            for j in range(fibers_per_region):
                y=region['y_m']+(i+.5)/fibers_per_region*region['width_m']-region['width_m']/2
                z=region['z_m']+(j+.5)/fibers_per_region*region['height_m']-region['height_m']/2
                fibers.append((y,z,region['width_m']*region['height_m']/fibers_per_region**2,role,law))
    target=np.asarray([demand['axial_n'],demand['moment_y_nm'],demand['moment_z_nm']],dtype=float)
    scales=np.maximum(np.abs(target),[1e5,1e5,1e5])
    concrete_states={role:concrete_state(law,age_days,temperature_c) for role,law in materials.items() if law['type']=='concrete'}
    def evaluate(q):
        forces=np.zeros(3);rows=[]
        for y,z,area,role,law in fibers:
            strain=q[0]+q[1]*z-q[2]*y;failure=False;index=None
            if law['type']=='concrete':
                state=concrete_states[role];stress,failure=concrete_stress(strain,state,characteristic_length_m)
            elif law['type']=='steel':
                result=steel_return(strain,law);stress=result['stress_pa'];index=abs(strain)/law['ultimate_strain'];failure=index>=1
            elif law['type']=='laminate':
                response=laminate_response(law['plies'],strain);stress=response['stress_pa']
                checks=[p['failure_index'] for p in response['ply_faces']]
                index=max(checks) if all(x is not None for x in checks) else None;failure=index is not None and index>=1
            else:raise ValueError('unregistered assembled material law')
            f=stress*area;forces+=f*np.array([1.,z,-y]);rows.append(dict(material=role,strain=float(strain),stress_pa=float(stress),failure_index=None if index is None else float(index),ultimate_exceeded=bool(failure)))
        return forces,rows
    initial=np.zeros(3)
    solution=least_squares(lambda q:(evaluate(q)[0]-target)/scales,initial,x_scale=[.001,.001,.001],max_nfev=200,xtol=1e-10,ftol=1e-10,gtol=1e-10)
    actual,rows=evaluate(solution.x);error=float(np.max(np.abs(actual-target)/scales))
    return dict(schema='osr-assembled-section-response/1',generalised_strains=solution.x.tolist(),demands=demand,
        resultant_n_nm=actual.tolist(),equilibrium_relative_error=error,equilibrium_solved=bool(solution.success and error<1e-5),
        fibers=rows,ultimate_exceeded=any(r['ultimate_exceeded'] for r in rows),
        local_strength_coverage_complete=all(law['type']!='laminate' or all(p.get(k) is not None for p in law['plies'] for k in ('Xt_pa','Xc_pa','Yt_pa','Yc_pa','S_pa')) for law in materials.values()),
        physical_validation=False,engineering_released=False,
        unresolved_checks=['shear resistance','local/distortional buckling','warping','reinforcement anchorage','fire/exposure durability'])


def rainflow(values):
    data=np.asarray(values,dtype=float)
    if data.ndim!=1 or len(data)<2 or not np.isfinite(data).all():raise ValueError('finite scalar fatigue history required')
    unique=[float(v) for i,v in enumerate(data) if i==0 or v!=data[i-1]]
    reversals=[unique[0]]+[unique[i] for i in range(1,len(unique)-1) if (unique[i]-unique[i-1])*(unique[i+1]-unique[i])<0]+[unique[-1]]
    stack=[];cycles=[]
    for point in reversals:
        stack.append(point)
        while len(stack)>=3:
            earlier=abs(stack[-2]-stack[-3]);recent=abs(stack[-1]-stack[-2])
            if earlier>recent:break
            if len(stack)==3:cycles.append(dict(range_pa=earlier,count=.5));stack.pop(0)
            else:cycles.append(dict(range_pa=earlier,count=1.));stack[-3:-1]=[]
    cycles.extend(dict(range_pa=abs(a-b),count=.5) for a,b in zip(stack,stack[1:]))
    return [r for r in cycles if r['range_pa']>0]
