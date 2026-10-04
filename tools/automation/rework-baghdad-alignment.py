#!/usr/bin/env python3
"""Rebuild controlled core corridors from an immutable pre-rework route seed.

Straight tangents and circular corner fillets replace street-following raster
zigzags. The grid is a planning representation; analytical tangent/arc controls
are preserved for subsequent survey and railway transition-curve design.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
CONFIG=ROOT/'lib/templates/baghdad-alignment.toml'
OUT=CITY/'engineering/alignment'
SEED=OUT/'pre-rework-corridors.json.gz'
GRID=OUT/'planning-grid.json'

def distance(a,b):return math.hypot(b[0]-a[0],b[1]-a[1])
def simplify(points,tolerance):
    if len(points)<3:return points
    a,b=points[0],points[-1];dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
    def error(p):
        t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
        return distance(p,(a[0]+t*dx,a[1]+t*dy))
    idx=max(range(1,len(points)-1),key=lambda i:error(points[i]))
    if error(points[idx])<=tolerance:return [a,b]
    return simplify(points[:idx+1],tolerance)[:-1]+simplify(points[idx:],tolerance)

def fillet(points,radius,spacing):
    controls=[];samples=[points[0]]
    def tangent(end):
        start=samples[-1];n=max(1,math.ceil(distance(start,end)/spacing))
        samples.extend((start[0]+(end[0]-start[0])*i/n,start[1]+(end[1]-start[1])*i/n) for i in range(1,n+1))
        controls.append(dict(kind='tangent',start=start,end=end,length_m=distance(start,end)))
    for a,b,c in zip(points,points[1:],points[2:]):
        ab,bc=distance(a,b),distance(b,c)
        if min(ab,bc)<1:continue
        u=((b[0]-a[0])/ab,(b[1]-a[1])/ab);v=((c[0]-b[0])/bc,(c[1]-b[1])/bc)
        angle=math.acos(max(-1,min(1,u[0]*v[0]+u[1]*v[1])))
        if angle<1e-5:continue
        if angle>=math.pi-.01:raise ValueError('Core alignment reverses direction; requires a new corridor')
        offset=min(radius*math.tan(angle/2),ab*.4,bc*.4)
        actual=offset/math.tan(angle/2)
        start=(b[0]-u[0]*offset,b[1]-u[1]*offset);end=(b[0]+v[0]*offset,b[1]+v[1]*offset)
        turn=1 if u[0]*v[1]-u[1]*v[0]>0 else -1
        center=(start[0]-turn*u[1]*actual,start[1]+turn*u[0]*actual)
        tangent(start);theta=math.atan2(start[1]-center[1],start[0]-center[0]);n=max(1,math.ceil(actual*angle/spacing))
        samples.extend((center[0]+actual*math.cos(theta+turn*angle*i/n),center[1]+actual*math.sin(theta+turn*angle*i/n)) for i in range(1,n+1))
        controls.append(dict(kind='arc',start=start,end=end,center=center,radius_m=actual,turn=turn,angle_rad=angle,length_m=actual*angle))
    tangent(points[-1]);return samples,controls

def rework(seed,grid,config):
    cell=seed['grid_cell_m'];core=config['core'];rows=[];result=json.loads(json.dumps(seed))
    def inside(rc):
        lat=grid['bbox_north']-rc[0]*cell/grid['m_per_deg_lat'];lon=grid['bbox_west']+rc[1]*cell/grid['m_per_deg_lon']
        return core['south']<=lat<=core['north'] and core['west']<=lon<=core['east']
    for line in result['lines']:
        original=line['cells'];segments=[];new=[];i=0
        while i<len(original):
            if not inside(original[i]):new.append(original[i]);i+=1;continue
            end=i+1
            while end<len(original) and inside(original[end]):end+=1
            points=[(r*cell,c*cell) for r,c in original[i:end]]
            if len(points)<3:new.extend(original[i:end]);i=end;continue
            waypoints=([points[0],points[-1]] if line['shape']=='Radial' and config['geometry']['straight_core_radials'] else simplify(points,config['geometry']['simplification_tolerance_m']))
            samples,controls=fillet(waypoints,config['geometry']['preferred_fillet_radius_m'],config['geometry']['sample_spacing_m'])
            cells=[[round(r/cell),round(c/cell)] for r,c in samples]
            for rc in cells:
                if not 0<=rc[0]<seed['grid_height'] or not 0<=rc[1]<seed['grid_width']:raise ValueError('Reworked corridor outside grid')
                if not new or rc!=new[-1]:new.append(rc)
            segments.append(dict(seed_from_index=i,seed_to_index=end-1,control_points=waypoints,controls=controls,
                original_length_m=sum(distance(a,b) for a,b in zip(points,points[1:])),analytical_length_m=sum(c['length_m'] for c in controls)))
            i=end
        line['cells']=new
        rows.append(dict(line=line['name'],original_cells=len(original),reworked_cells=len(new),
            original_route_m=sum(distance(a,b)*cell for a,b in zip(original,original[1:])),
            reworked_route_m=sum(distance(a,b)*cell for a,b in zip(new,new[1:])),core_runs=segments))
    return result,dict(schema_version=1,status=config['release']['status'],core=core,lines=rows,
        core_original_length_m=sum(s['original_length_m'] for l in rows for s in l['core_runs']),
        core_analytical_length_m=sum(s['analytical_length_m'] for l in rows for s in l['core_runs']),
        limitations=['Elevated rail does not grant air/property rights or remove buildings. Survey, clearance, heritage/security restrictions, pier access and utilities remain open.',
            'Circular planning fillets need cant, transition curves, vertical alignment and independent review; a rounded raster is not a construction centerline.',
            'Water stays separately engineered bridge scope; station/interchange placement, fleet, civil quantities and cost must be regenerated.'])

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    seed=json.loads(gzip.decompress(SEED.read_bytes()));grid=json.loads(GRID.read_text());config=tomllib.loads(CONFIG.read_text())
    corridors,report=rework(seed,grid,config)
    report['sources_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),CONFIG,SEED,GRID]}
    # Sub-micrometre libm differences across supported Python versions must
    # not change planning-report bytes. Grid cells remain exact integers.
    def planning_precision(value):
        if isinstance(value,float):return round(value,6)
        if isinstance(value,list):return [planning_precision(item) for item in value]
        if isinstance(value,tuple):return [planning_precision(item) for item in value]
        if isinstance(value,dict):return {key:planning_precision(item) for key,item in value.items()}
        return value
    report=planning_precision(report)
    files={CITY/'corridors.json':json.dumps(corridors,indent=2)+'\n',OUT/'core-realignment.json':json.dumps(report,indent=2,sort_keys=True)+'\n',CITY/'alignment-policy.toml':CONFIG.read_text()}
    for p,text in files.items():
        if args.check:
            if p.read_text()!=text:raise ValueError('Stale core alignment: '+str(p))
        else:p.write_text(text)
    print(f"Core analytical corridor: {report['core_original_length_m']/1000:.3f} → {report['core_analytical_length_m']/1000:.3f} km; city-centre civil policy: elevated except water")
if __name__=='__main__':main()
