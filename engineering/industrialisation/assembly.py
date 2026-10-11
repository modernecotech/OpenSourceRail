"""Datum, tolerance and capacity planning with explicit production boundaries."""
from __future__ import annotations
import math
import numpy as np
from .common import finite,fingerprint


def fixture_constraints(points_m,normals):
    if any(isinstance(v,(bool,np.bool_)) for data in (points_m,normals) for v in np.asarray(data,dtype=object).flat):
        raise ValueError('boolean locator coordinates are not physical dimensions')
    points=np.asarray(points_m);directions=np.asarray(normals)
    if points.dtype.kind not in 'if' or directions.dtype.kind not in 'if':raise ValueError('numeric locator points and directions required')
    points=points.astype(float);directions=directions.astype(float)
    if points.shape!=(6,3) or directions.shape!=(6,3) or not np.isfinite(points).all() or not np.isfinite(directions).all():
        raise ValueError('six finite locator points and directions required')
    if not np.allclose(np.linalg.norm(directions,axis=1),1.,rtol=0.,atol=1e-10):raise ValueError('unit locator normals required')
    J=np.hstack([directions,np.cross(points,directions)])
    rank=int(np.linalg.matrix_rank(J,tol=1e-10))
    return dict(constraint_rank=rank,independent_rigid_body_restraints=rank==6,matrix=J.tolist(),
        fixture_released=False,limits=['kinematic rank only; clamp forces, contact stiffness, wear and load capacity require separate evidence'])


def battery_fixture(pack):
    L,W,H=pack['dimensions_m']
    points=[[-.4*L,-.3*W,0.],[.4*L,-.3*W,0.],[0.,.3*W,0.],[-.35*L,W/2,H/2],[.35*L,W/2,H/2],[L/2,0.,H/2]]
    normals=[[0.,0.,1.]]*3+[[0.,-1.,0.]]*2+[[-1.,0.,0.]]
    primitives=[]
    for i,p in enumerate(points):
        axis='z' if i<3 else 'y' if i<5 else 'x';centre=p.copy();j='xyz'.index(axis)
        centre[j]+=-.02 if i<3 else .02
        primitives.append(dict(id=f'locator-{i+1}',kind='cylinder',centre_m=centre,radius_m=.02,length_m=.04,axis=axis))
    for sign in (-1,1):primitives.append(dict(id=f'base-rail-{sign}',kind='box',centre_m=[0.,sign*.3*W,-.08],dimensions_m=[L+.16,.08,.08]))
    primitives.append(dict(id='base-cross-member',kind='box',centre_m=[0.,0.,-.08],dimensions_m=[.08,W+.16,.08]))
    upright_height=H/2+.07;upright_z=-.04+upright_height/2
    for sign in (-1,1):
        primitives.append(dict(id=f'side-locator-mount-{sign}',kind='box',centre_m=[sign*.35*L,W/2+.06,upright_z],dimensions_m=[.08,.04,upright_height]))
        reach=W/2+.06-.3*W
        primitives.append(dict(id=f'side-outrigger-{sign}',kind='box',centre_m=[sign*.35*L,.3*W+reach/2,-.08],dimensions_m=[.08,reach+.08,.08]))
    primitives.append(dict(id='end-cross-member',kind='box',centre_m=[L/2+.04,0.,-.08],dimensions_m=[.08,W+.16,.08]))
    primitives.append(dict(id='end-locator-mount',kind='box',centre_m=[L/2+.06,0.,upright_z],dimensions_m=[.04,.08,upright_height]))
    check=fixture_constraints(points,normals)
    return dict(schema='osr-battery-fixture-reference/1',id='OSR-IM-FIX-BAT-01',battery_geometry_sha256=fingerprint(pack['geometry']),
        locator_points_m=points,locator_normals=normals,geometry=dict(role='battery-datum-fixture',primitives=primitives),
        checks=check,inspection_targets=['locator survey','base twist','repeatability','removal and tool access','clamp/load test'],
        fixture_released=False,physical_validation=False)


def tolerance_stack(terms,minimum_m,maximum_m,*,independent_uncertainties=False):
    if not terms:raise ValueError('nonempty functional tolerance chain required')
    nominal=radius=variance=0.;all_uncertainties=True
    for row in terms:
        if set(row)!={'id','nominal_m','tolerance_m','coefficient','standard_uncertainty_m','thermal_offset_m'} or not row['id']:
            raise ValueError('complete tolerance term required')
        x=finite(row['nominal_m'],'stack nominal');tol=finite(row['tolerance_m'],'tolerance half-width',0.)
        coefficient=finite(row['coefficient'],'stack coefficient');thermal=finite(row['thermal_offset_m'],'declared thermal offset')
        nominal+=coefficient*(x+thermal);radius+=abs(coefficient)*tol
        sigma=row['standard_uncertainty_m']
        if sigma is None:all_uncertainties=False
        else:variance+=(coefficient*finite(sigma,'standard uncertainty',0.))**2
    lo,hi=nominal-radius,nominal+radius
    if minimum_m is None or maximum_m is None:within=None
    else:
        a,b=finite(minimum_m,'allowed clearance'),finite(maximum_m,'allowed clearance')
        if a>b:raise ValueError('ordered functional clearance limits required')
        within=a<=lo and hi<=b
    return dict(nominal_m=nominal,worst_case_interval_m=[lo,hi],within_declared_clearance=within,
        rss_standard_uncertainty_m=math.sqrt(variance) if independent_uncertainties is True and all_uncertainties else None,
        production_released=False,limits=['tolerance bounds are not standard deviations','thermal offsets must come from a released temperature/material model','RSS requires declared independent standard uncertainties'])


def schedule(operations,capacities):
    """Deterministic list scheduling with resource slots and mandatory wait times."""
    nodes={r['id']:r for r in operations}
    if len(nodes)!=len(operations) or not nodes:raise ValueError('unique nonempty operation identities required')
    for resource,capacity in capacities.items():
        if not resource or type(capacity) is not int or capacity<1:raise ValueError('positive resource capacity required')
    for row in operations:
        if len(row['predecessors'])!=len(set(row['predecessors'])) or not set(row['predecessors'])<=set(nodes) or row['id'] in row['predecessors']:
            raise ValueError('operation predecessor identity invalid')
        if row['resource'] not in capacities:raise ValueError('operation resource has no capacity')
        finite(row['duration_minutes'],'operation duration',1e-9);finite(row['minimum_wait_minutes'],'minimum process wait',0.)
    slots={k:[0.]*v for k,v in capacities.items()};pending=set(nodes);done={};rows=[]
    while pending:
        eligible=[]
        for identifier in pending:
            row=nodes[identifier]
            if not set(row['predecessors'])<=set(done):continue
            earliest=max((done[p] for p in row['predecessors']),default=0.)+row['minimum_wait_minutes']
            slot=min(range(len(slots[row['resource']])),key=lambda i:(slots[row['resource']][i],i))
            eligible.append((max(earliest,slots[row['resource']][slot]),identifier,slot))
        if not eligible:raise ValueError('cyclic assembly/production dependency')
        start,identifier,slot=min(eligible);row=nodes[identifier];end=start+row['duration_minutes']
        slots[row['resource']][slot]=end;done[identifier]=end;pending.remove(identifier)
        rows.append(dict(id=identifier,resource=row['resource'],resource_slot=slot,start_minutes=start,finish_minutes=end,
            predecessors=row['predecessors'],minimum_wait_minutes=row['minimum_wait_minutes']))
    return dict(schema='osr-production-resource-schedule/1',operations=rows,makespan_minutes=max(done.values()),
        capacity=capacities,production_forecast_qualified=False,limits=['planning durations; released cure/dry windows and actual measured cycles control production','labour shifts, transport and breakdowns require separate planning inputs'])
