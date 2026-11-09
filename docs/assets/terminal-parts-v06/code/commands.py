"""Literal sealed SI primitives to recorded SolidCraft commands, INPUT ONLY."""
from math import isfinite
from geometry import world,as_csg,dot,cross
from geometry import read,check,seal,FLAGS
from pathlib import Path
import joins

def cmd(name,params):return dict(command=name,params=params)
def mm(v):return [1000*x for x in v]
def validate_frame(g):
    if g['kind']=='difference':
        validate_frame(g['outer']);validate_frame(g['void']);return
    R=g['rotation']
    if len(R)!=3 or any(len(r)!=3 for r in R) or any(not isfinite(x) for r in R for x in r):raise ValueError('Finite 3x3 rigid frame required')
    if any(abs(dot(a,b)-(1. if i==j else 0.))>1e-12 for i,a in enumerate(R) for j,b in enumerate(R)) or dot(R[0],cross(R[1],R[2]))<1-1e-12:raise ValueError('Proper orthonormal rigid frame required')
    if len(g['at_m'])!=3 or any(not isfinite(x) for x in g['at_m']):raise ValueError('Finite explicit origin required')
def cylinder(radius,length,at,axis,name,target):
    if min(radius,length)<=0 or abs(dot(axis,axis)-1)>1e-12:raise ValueError('Positive cylinder and unit axis required')
    p=dict(radius=radius*1000,height=length*1000,base=mm(at),axis=axis,operation='cut' if target else 'new')
    p.update(targets=[target]) if target else p.update(body_name=name)
    return cmd('solid.cylinder',p)
def primitive(g,name,target=None):
    g=as_csg(g);validate_frame(g);k=g['kind']
    if k=='difference':return primitive(g['outer'],name,target)+primitive(g['void'],name,name)
    if k=='annulus':
        axis=[r[0] for r in g['rotation']];base=world(g,[-g['length_m']/2,0,0])
        out=[cylinder(g['outer_diameter_m']/2,g['length_m'],base,axis,name,target)]
        if g['inner_diameter_m']>0:out.append(cylinder(g['inner_diameter_m']/2,g['length_m'],base,axis,name,name))
        return out
    if k=='box':
        L,W,H=g['size_m'];points=[[-W/2,-H/2],[W/2,-H/2],[W/2,H/2],[-W/2,H/2]]
    elif k=='profile-prism':L=g['length_m'];points=g['points_yz_m']
    else:raise ValueError('Unsupported literal primitive '+k)
    p=dict(distance=L*1000,operation='cut' if target else 'new')
    p.update(targets=[target]) if target else p.update(body_name=name)
    return [cmd('sketch.create',dict(plane=dict(origin=mm(world(g,[-L/2,0,0])),x_dir=[r[1] for r in g['rotation']],y_dir=[r[2] for r in g['rotation']]),name='section '+name)),cmd('sketch.line',dict(points=[mm(v) for v in points],closed=True,infer=False)),cmd('sketch.finish',{}),cmd('solid.extrude',p)]
def serialize(spec,registry=None):
    registry=registry if registry is not None else check(read(Path(__file__).resolve().parents[1]/'join-registry.json'))
    converted=[];reports=[]
    for p in spec['primitives']:
        g,rows=joins.primitive(p,spec,registry);converted.append((p,g));reports.extend(rows)
    report=seal(dict(schema='osr-terminal-native-numerical-join-serialization/1',physical_definition_id=spec['physical_definition_id'],source_geometry_evaluation_id=spec['source_geometry_evaluation_id'],registry_evaluation_id=registry['evaluation_id'],profiles=reports,original_physical_source_geometry_unchanged=True,nominal_quantity_oracle_unchanged=True,finite_vertices_moved=0,engineering_tolerance_relaxed=False,**FLAGS))
    result=[cmd('document.units',dict(units='mm')),cmd('document.metadata.set',dict(values={'org.opensourcerail.terminal-part-diagnostic':dict(physical_definition_id=spec['physical_definition_id'],source_geometry_evaluation_id=spec['source_geometry_evaluation_id'],serializer='terminal-native-adjacent-join-v2',serialization_evaluation_id=report['evaluation_id'],display_offsets_applied=False,scope='Individual exact declared part solids; split compound subpieces remain distinct; no installed assembly acceptance')}))]
    for p,g in converted:
        result.extend(primitive(g,p['native_body_id']))
        for h in p['holes']:result.append(cylinder(h['diameter_m']/2,h['length_m'],h['at_m'],h['axis'],None,p['native_body_id']))
    result.append(cmd('inspect.measure',{}));return dict(commands=result),report
def script(spec):return serialize(spec)[0]
