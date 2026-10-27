"""Explicit numerical entry-window mesh; all physical motor boundaries remain.

The entry-window streamwise cells and secondary/gap layers are independent
variables. Remote primary, steel and air construction rules stay fixed across
these local comparisons. This is not a whole-domain convergence certificate.
"""
from math import ceil,isfinite
import numpy as np
from engineering.station_rail.common import identity

CODE='engineering/design_search/lim_critical_mesh.py'
NAME='entry-local-tensor'


def definition(critical_dx_m=.02,secondary_dy_m=.00375):
    if any(type(x) not in (int,float) or not isfinite(x) for x in (critical_dx_m,secondary_dy_m)) or not .0025<=critical_dx_m<=.04 or not .00046875<=secondary_dy_m<=.0075:
        raise ValueError('Finite bounded critical streamwise/secondary mesh targets required')
    d=dict(schema='osr-LIM-critical-mesh/1',name=NAME,critical_dx_m=critical_dx_m,secondary_dy_m=secondary_dy_m,
        critical_window_m=[-.5,1.],far_primary_dx_m=.08,far_air_dx_m=.15,steel_dy_m=.02,outer_air_dy_m=.04,
        end_face_fringe_margin_m=.25,all_material_boundaries_conforming=True,
        physical_geometry_changed=False,scope='Local critical-region numerical refinement; remote mesh and physical qualification remain open')
    d['mesh_definition_id']=identity(d);return d


def _parts(edges,target):
    edges=sorted(set(round(float(x),12) for x in edges));out=[]
    for a,b in zip(edges,edges[1:]):
        h=target((a+b)/2)
        # Remove floating-point integer-ratio accidents, without permitting a
        # material interface or a real target subdivision to disappear.
        n=max(1,ceil((b-a)/h-1e-10));out.extend(np.linspace(a,b,n+1)[:-1])
    return np.r_[out,edges[-1]]


def axes(r):
    d=r['mesh_definition'];expected=definition(d['critical_dx_m'],d['secondary_dy_m'])
    if d!=expected:raise ValueError('Critical mesh construction/domain differs')
    p=r['physical_geometry'];L=p['primary_length_m'];fin=p['secondary_length_m'];pitch=2*p['pole_pitch_m']/6
    end=r['start_m']+r['speed_m_s']*r['dt_s']*r['steps'];window=d['critical_window_m'];margin=d['end_face_fringe_margin_m']
    if min(r['start_m']+fin,end+fin)<window[0]+margin or max(r['start_m']+fin,end+fin)>window[1]-margin:
        raise ValueError('Entry-window mesh does not cover the declared moving end face and fringe margin')
    lo=min(-.5,r['start_m']-.5,end-.5);hi=max(L+.5,r['start_m']+fin+.5,end+fin+.5)
    edges=[lo,0.,L,hi,*window]
    for k in range(p['periods']*6):
        middle=(k+.5)*pitch;edges.extend([middle-p['slot_width_m']/2,middle+p['slot_width_m']/2])
    def target(x):
        if window[0]<x<window[1]:return d['critical_dx_m']
        return d['far_primary_dx_m'] if 0<x<L else d['far_air_dx_m']
    x=_parts(edges,target)
    half=p['secondary_thickness_m']/2;face=half+p['gap_each_side_m'];back=face+p['slot_depth_m'];outer=back+p['backiron_m']
    y=_parts([-outer-.2,-outer,-back,-face,-half,half,face,back,outer,outer+.2],
        lambda a:d['secondary_dy_m'] if abs(a)<face else d['steel_dy_m'] if abs(a)<outer else d['outer_air_dy_m'])
    return x,y


def diagnostics(r,x,y):
    p=r['physical_geometry'];d=r['mesh_definition'];dx=np.diff(x);dy=np.diff(y);half=p['secondary_thickness_m']/2
    front=r['start_m']+p['secondary_length_m'];last=front+r['speed_m_s']*r['dt_s']*r['steps']
    engaged=(x[:-1]<min(p['primary_length_m'],max(front,last)))&(x[1:]>max(0.,min(r['start_m'],r['start_m']+r['speed_m_s']*r['dt_s']*r['steps'])))
    band=(y[:-1]>=-half-1e-12)&(y[1:]<=half+1e-12)
    critical=(x[:-1]>=d['critical_window_m'][0]-1e-12)&(x[1:]<=d['critical_window_m'][1]+1e-12)
    return dict(mesh_definition_id=d['mesh_definition_id'],critical_window_m=d['critical_window_m'],
        maximum_dx_in_critical_window_m=float(max(dx[critical])),
        maximum_dx_in_engaged_primary_m=float(max(dx[engaged])),
        unique_dx_in_engaged_primary_m=sorted(set(round(v,12) for v in dx[engaged])),
        maximum_dy_in_secondary_m=float(max(dy[band])),secondary_y_intervals=int(sum(band)),
        remote_mesh_fixed=True,whole_domain_convergence_established=False)
