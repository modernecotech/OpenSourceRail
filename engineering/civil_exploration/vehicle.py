"""Vertical modal bridge coupled to sprung/unsprung axle oscillators.

This research diagnostic resolves suspension/contact force feedback. It uses
ideal simply supported modes and a linear compressive contact domain; negative
contact forces are reported as outside that domain, never silently accepted.
"""
from __future__ import annotations
import math
import numpy as np
from .nonlinear import curve_file


def matrices(EI,mass_per_m,length,modes,vehicle,positions):
    n=len(positions);size=modes+2*n
    M=np.zeros((size,size));K=np.zeros_like(M);C=np.zeros_like(M);F=np.zeros(size)
    frequencies=np.asarray([(i*math.pi/length)**2*math.sqrt(EI/mass_per_m) for i in range(1,modes+1)])
    modal_mass=mass_per_m*length/2
    M[:modes,:modes]=np.eye(modes)*modal_mass
    K[:modes,:modes]=np.diag(modal_mass*frequencies**2)
    C[:modes,:modes]=np.diag(2*vehicle['bridge_damping_ratio']*frequencies*modal_mass)
    for axle,x in enumerate(positions):
        s,u=modes+2*axle,modes+2*axle+1
        ms,mu,ks,cs,kc=(vehicle[k] for k in ('sprung_mass_kg','unsprung_mass_kg','suspension_n_m','suspension_ns_m','contact_n_m'))
        M[s,s]=ms;M[u,u]=mu
        K[s,s]+=ks;K[u,u]+=ks;K[s,u]-=ks;K[u,s]-=ks
        C[s,s]+=cs;C[u,u]+=cs;C[s,u]-=cs;C[u,s]-=cs
        if 0<x<length:
            phi=np.asarray([math.sin(i*math.pi*x/length) for i in range(1,modes+1)])
            K[:modes,:modes]+=kc*np.outer(phi,phi)
            K[:modes,u]-=kc*phi;K[u,:modes]-=kc*phi;K[u,u]+=kc
            F[:modes]+=phi*(ms+mu)*9.81
            roughness=vehicle['irregularity_amplitude_m']*math.sin(2*math.pi*x/vehicle['irregularity_wavelength_m'])
            F[:modes]-=kc*phi*roughness;F[u]+=kc*roughness
        else:
            # Off-span axle follows a rigid approach track.
            K[u,u]+=kc
    return M,C,K,F


def run(EI,mass_per_m,length,offsets,vehicle,*,speed=20.,dt=.002,modes=8,output=None):
    fields={'sprung_mass_kg','unsprung_mass_kg','suspension_n_m','suspension_ns_m','contact_n_m',
            'bridge_damping_ratio','irregularity_amplitude_m','irregularity_wavelength_m','basis'}
    if set(vehicle)!=fields or not vehicle['basis'] or not all(type(v) in (int,float) and math.isfinite(v) and v>=0 for k,v in vehicle.items() if k!='basis'):
        raise ValueError('coupled vehicle input contract invalid')
    if min(EI,mass_per_m,length,speed,dt,vehicle['sprung_mass_kg'],vehicle['unsprung_mass_kg'],vehicle['suspension_n_m'],vehicle['contact_n_m'],vehicle['irregularity_wavelength_m'])<=0:
        raise ValueError('coupled vehicle dimensions/properties must be positive')
    if type(modes) is not int or not 1<=modes<=25 or not .0002<=dt<=.02 or not 0<speed<=50 or len(offsets)>100:
        raise ValueError('coupled vehicle discretisation outside bounded domain')
    size=modes+2*len(offsets);q=np.zeros(size);velocity=np.zeros(size);acceleration=np.zeros(size)
    count=math.ceil((length+max(offsets))/speed/dt)
    rows=[];minimum_contact=math.inf;maximum_contact=0.
    beta=.25;gamma=.5
    for step in range(1,count+1):
        t=step*dt;positions=[speed*t-offset for offset in offsets]
        M,C,K,F=matrices(EI,mass_per_m,length,modes,vehicle,positions)
        predicted=q+dt*velocity+dt*dt*(.5-beta)*acceleration
        predicted_velocity=velocity+dt*(1-gamma)*acceleration
        effective=M+gamma*dt*C+beta*dt*dt*K
        new_acceleration=np.linalg.solve(effective,F-C@predicted_velocity-K@predicted)
        q=predicted+beta*dt*dt*new_acceleration;velocity=predicted_velocity+gamma*dt*new_acceleration;acceleration=new_acceleration
        midpoint=np.asarray([math.sin(i*math.pi/2) for i in range(1,modes+1)])
        contact=[]
        for axle,x in enumerate(positions):
            if 0<x<length:
                phi=np.asarray([math.sin(i*math.pi*x/length) for i in range(1,modes+1)])
                roughness=vehicle['irregularity_amplitude_m']*math.sin(2*math.pi*x/vehicle['irregularity_wavelength_m'])
                force=(vehicle['sprung_mass_kg']+vehicle['unsprung_mass_kg'])*9.81+vehicle['contact_n_m']*(q[modes+2*axle+1]-phi@q[:modes]-roughness)
                contact.append(float(force))
        if contact:minimum_contact=min(minimum_contact,min(contact));maximum_contact=max(maximum_contact,max(contact))
        rows.append(dict(time_s=t,midpoint_displacement_m=float(midpoint@q[:modes]),midpoint_acceleration_m_s2=float(midpoint@acceleration[:modes]),
                         minimum_contact_n=min(contact) if contact else 0.,maximum_contact_n=max(contact) if contact else 0.))
    if output:curve_file(output,rows)
    return dict(schema='osr-civil-coupled-vehicle/1',peak_displacement_m=max(abs(r['midpoint_displacement_m']) for r in rows),
                peak_acceleration_m_s2=max(abs(r['midpoint_acceleration_m_s2']) for r in rows),
                minimum_contact_n=minimum_contact if math.isfinite(minimum_contact) else None,maximum_contact_n=maximum_contact,
                status='within-linear-contact-domain' if minimum_contact>=0 else 'outside-compressive-contact-domain',
                vehicle=vehicle,speed_m_s=speed,time_step_s=dt,modes=modes,axle_count=len(offsets),physical_release=False,
                bridge_inputs=dict(EI_nm2=EI,mass_kg_m=mass_per_m,span_m=length,axle_offsets_m=list(offsets)),
                gaps=['supplier sprung/unsprung/suspension records','validated rail irregularity','contact loss nonlinear model','lateral/3D vehicle interaction','flexible multi-span modal calibration'])
