"""Exact retained isotropic J(H) proxy; mathematical, not material validation."""
import math
import numpy as np

MU0=4e-7*math.pi
LOW_H=1e-6
LOW_MU=MU0+.0025


def table(steel):
    h=np.asarray(steel['h_a_m'],dtype=float);j=np.asarray(steel['j_t'],dtype=float)
    if h.ndim!=1 or j.shape!=h.shape or len(h)<2 or not np.isfinite(h).all() or not np.isfinite(j).all() or h[0]!=0 or j[0]!=0 or h[-1]!=100000 or np.any(np.diff(h)<=0):
        raise ValueError('retained finite monotonic J(H) table with 100000 A/m clamp required')
    return h,j


def flux_density(H,steel):
    H=np.asarray(H,dtype=float)
    if H.shape!=(3,) or not np.isfinite(H).all():raise ValueError('finite 3-vector H required')
    h,j=table(steel);r=float(np.linalg.norm(H));mu=LOW_MU if r<LOW_H else MU0+float(np.interp(min(r,100000.),h,j))/r
    return mu*H


def tangent(H,steel):
    H=np.asarray(H,dtype=float)
    if H.shape!=(3,) or not np.isfinite(H).all():raise ValueError('finite 3-vector H required')
    h,j=table(steel);r=float(np.linalg.norm(H))
    if r<LOW_H:return LOW_MU*np.eye(3)
    J=float(np.interp(min(r,100000.),h,j));index=min(len(h)-2,max(0,int(np.searchsorted(h,r,side='right'))-1));slope=0. if r>100000. else float((j[index+1]-j[index])/(h[index+1]-h[index]))
    return (MU0+J/r)*np.eye(3)+(slope-J/r)/(r*r)*np.outer(H,H)


def fixture(steel):
    h,_=table(steel);direction=np.array([1.,2.,-3.])/np.sqrt(14);norms=[0.,.25e-6,.5e-6,2e-6/3,.99e-6,1.01e-6,10.,35.,70.,175.,750.,7500.,45000.,125000.];rows=[]
    for radius in norms:
        H=radius*direction;barriers=np.r_[h,LOW_H];distance=min(abs(radius-x) for x in barriers if x!=radius);base=1e-8 if radius==0 else min(max(radius,LOW_H)*1e-3,.1*distance);errors=[]
        for scale in (1.,.1,.01):
            step=base*scale;fd=np.column_stack([(flux_density(H+step*np.eye(3)[axis],steel)-flux_density(H-step*np.eye(3)[axis],steel))/(2*step) for axis in range(3)])
            errors.append(float(np.linalg.norm(tangent(H,steel)-fd,ord=2)/np.linalg.norm(fd,ord=2)))
        rows.append(dict(H_A_per_m=H.tolist(),relative_operator_errors=errors))
    return dict(schema='osr-steel-tangent-confirmation/1',records=rows,relative_error_screen=1e-5,passed=all(max(x['relative_operator_errors'])<1e-5 for x in rows),material_curve_validated=False,physical_accepted=False,scope='Central finite differences of retained B(H) only; no measured steel or force credit')
