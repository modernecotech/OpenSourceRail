"""Geometry-specific six-resultant bolt-group loads and elastic compliance."""
from __future__ import annotations
import math
import numpy as np
from engineering.industrialisation.common import finite,fingerprint


def bolt_group(positions_m,diameter_m,grip_m,youngs_pa,poisson=.3):
    p=np.asarray(positions_m,dtype=float)
    if p.ndim!=2 or p.shape[1]!=3 or len(p)<3 or not np.isfinite(p).all():raise ValueError('three or more finite bolt positions required')
    if len({tuple(row) for row in p})!=len(p):raise ValueError('duplicate bolt position')
    d=finite(diameter_m,'bolt diameter',1e-9);L=finite(grip_m,'grip',1e-9);E=finite(youngs_pa,'bolt modulus',1.)
    nu=finite(poisson,'Poisson ratio',0.)
    if nu>=.5:raise ValueError('supported isotropic Poisson ratio required')
    A=math.pi*d*d/4;G=E/(2*(1+nu));local=np.diag([G*A/L,G*A/L,E*A/L]);K=np.zeros((6,6));maps=[]
    for x,y,z in p:
        cross=np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])
        B=np.hstack([np.eye(3),-cross]);K+=B.T@local@B;maps.append(B)
    if np.linalg.eigvalsh(K).min()<=0:raise ValueError('bolt group cannot restrain six resultants')
    return dict(schema='osr-elastic-bolt-group/1',positions_m=p.tolist(),shank_area_m2=A,
        local_stiffness_n_m=local.tolist(),stiffness_si=K.tolist(),maps=[B.tolist() for B in maps],
        source='original elastic shank model; declared geometry/modulus; threads, prying and members not inferred',
        qualified=False,physical_validation=False)


def assess(group,force_moment_si,*,preload_n=None,friction=None,tensile_capacity_n=None,shear_capacity_n=None):
    load=np.asarray(force_moment_si,dtype=float)
    if load.shape!=(6,) or not np.isfinite(load).all():raise ValueError('simultaneous finite force/moment six-vector required')
    K=np.asarray(group['stiffness_si']);u=np.linalg.solve(K,load);local=np.asarray(group['local_stiffness_n_m'])
    forces=[local@np.asarray(B)@u for B in group['maps']]
    recovered=sum((np.asarray(B).T@f for B,f in zip(group['maps'],forces)),np.zeros(6))
    error=float(np.linalg.norm(recovered-load)/max(1.,np.linalg.norm(load)))
    if error>1e-10:raise ValueError('bolt-group resultant recovery failed')
    for value,name in [(preload_n,'preload'),(friction,'friction'),(tensile_capacity_n,'tension capacity'),(shear_capacity_n,'shear capacity')]:
        if value is not None:finite(value,name,0.)
    tension=max(max(0.,f[2]) for f in forces);shear=max(float(np.linalg.norm(f[:2])) for f in forces)
    if preload_n is None or friction is None:slip=None;separation=None
    else:
        # Conservative declared screen; member stiffness/load fraction and
        # torque-to-preload qualification still need an actual joint model.
        separation=any(f[2]>=preload_n for f in forces)
        slip=any(np.linalg.norm(f[:2])>friction*max(0.,preload_n-f[2]) for f in forces)
    strength=None if tensile_capacity_n is None or shear_capacity_n is None else tension<=tensile_capacity_n and shear<=shear_capacity_n
    return dict(schema='osr-joint-demand-screen/1',group_sha256=fingerprint(group),load_si=load.tolist(),
        relative_pose_si=u.tolist(),bolt_forces_n=[f.tolist() for f in forces],resultant_relative_error=error,
        peak_tension_n=float(tension),peak_shear_n=shear,slip_screen_failed=slip,separation_screen_failed=separation,
        within_declared_strength=strength,ready_for_independent_review=all(v is not None for v in (slip,separation,strength)) and not slip and not separation and strength,
        capacity_qualified=False,physical_validation=False,production_released=False,
        open_domains=['thread stress area','member/prying compliance','approved preload/locking','fatigue and corrosion','physical joint correlation'])


def battery_mount(pack,inputs):
    positions=[list(point) for point in pack['hole_pattern_m']]
    return bolt_group(positions,inputs['diameter_m'],inputs['grip_m'],inputs['youngs_pa'])
