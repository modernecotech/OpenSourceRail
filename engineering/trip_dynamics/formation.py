"""Actual Chrono rigid bodies/couplers; x forward, y left, z up.

The optional ideal support constrains five DOFs. It is a benchmark fixture,
not magnetic levitation, guidance, body flexibility or physical qualification.
"""
from hashlib import sha256
import json
import math


def identity(value):
    return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()


def definition(masses_kg, *, body_length_m=17., coupling_gap_m=.5,
               coupler_stiffness_N_per_m=1.e6, coupler_damping_Ns_per_m=1.e5):
    masses=list(masses_kg)
    if not masses or len(masses)>6 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in masses):
        raise ValueError('one to six finite positive car masses required')
    values=(body_length_m,coupling_gap_m,coupler_stiffness_N_per_m,coupler_damping_Ns_per_m)
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in values):
        raise ValueError('finite positive body, gap and coupler parameters required')
    value=dict(schema='osr-chrono-formation/1',masses_kg=masses,body_length_m=body_length_m,
        body_width_m=2.8,body_height_m=3.2,coupling_gap_m=coupling_gap_m,
        coupler_stiffness_N_per_m=coupler_stiffness_N_per_m,coupler_damping_Ns_per_m=coupler_damping_Ns_per_m,
        inertia_scope='Uniform rigid cuboid hypothesis; actual installed inertia unknown',
        coupler_scope='Linear axial spring/damper benchmark; actual coupler design/rating unknown',
        frame='right-handed x forward, y left, z up')
    value['vehicle_id']=identity(value)
    return value


def build(system, chrono, masses_kg, *, ideal_support=True, **parameters):
    spec=definition(masses_kg,**parameters);L=spec['body_length_m'];gap=spec['coupling_gap_m']
    ground=chrono.ChBody();ground.SetName('ideal-fixed-reference');ground.SetFixed(True);ground.EnableCollision(False);system.AddBody(ground)
    bodies=[];supports=[];accumulators=[];initial=[]
    for i,mass in enumerate(spec['masses_kg']):
        body=chrono.ChBody();body.SetName('car-'+str(i+1));body.SetMass(mass);body.EnableCollision(False)
        width,height=spec['body_width_m'],spec['body_height_m']
        body.SetInertiaXX(chrono.ChVector3d(mass*(width**2+height**2)/12,mass*(L**2+height**2)/12,mass*(L**2+width**2)/12))
        x=-i*(L+gap);initial.append(x);body.SetPos(chrono.ChVector3d(x,0,0));system.AddBody(body)
        accumulators.append(body.AddAccumulator());bodies.append(body)
        if ideal_support:
            support=chrono.ChLinkMateGeneric(False,True,True,True,True,True)
            support.SetName('ideal-five-DOF-support-'+str(i+1));support.Initialize(body,ground,chrono.ChFramed(body.GetPos()));system.AddLink(support);supports.append(support)
    couplers=[]
    for i in range(len(bodies)-1):
        link=chrono.ChLinkTSDA();link.SetName('coupler-'+str(i+1))
        link.Initialize(bodies[i],bodies[i+1],True,chrono.ChVector3d(-L/2,0,0),chrono.ChVector3d(L/2,0,0))
        link.SetRestLength(gap);link.SetSpringCoefficient(spec['coupler_stiffness_N_per_m']);link.SetDampingCoefficient(spec['coupler_damping_Ns_per_m']);system.AddLink(link);couplers.append(link)
    return dict(definition=spec,bodies=bodies,couplers=couplers,supports=supports,ground=ground,accumulators=accumulators,initial_positions_m=initial)
