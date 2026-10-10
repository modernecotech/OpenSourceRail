"""Small, controlled reference solids shared by CAD and the variant compiler.

These primitives describe OSR study geometry, never supplier internal geometry.
Embedding the specification in the instance source binds CAD to its model hash.
"""
from __future__ import annotations
import json
import math
import numpy as np

PREFIX = 'osr-parametric-reference/1:'


def validate_spec(spec):
    if set(spec) != {'role', 'primitives'} or not isinstance(spec['role'], str) or not spec['role']:
        raise ValueError('reference geometry role and primitives required')
    if not isinstance(spec['primitives'], list) or not 1 <= len(spec['primitives']) <= 512:
        raise ValueError('reference geometry primitive budget exceeded')
    for p in spec['primitives']:
        common = {'id', 'kind', 'centre_m'}
        specific = {'box': {'dimensions_m'}, 'plate': {'dimensions_m', 'holes_xy_m', 'hole_radius_m'}, 'cylinder': {'radius_m', 'length_m', 'axis'},
                    'tube': {'radius_m', 'inner_radius_m', 'length_m', 'axis'}}
        if p.get('kind') not in specific or set(p) != common | specific[p['kind']]:
            raise ValueError('unsupported reference primitive fields')
        if not isinstance(p['id'], str) or not p['id'] or len(p['centre_m']) != 3:
            raise ValueError('primitive identity and centre required')
        values = list(p['centre_m'])
        if p['kind'] in ('box','plate'):
            if len(p['dimensions_m']) != 3:raise ValueError('three box dimensions required')
            dimensions = p['dimensions_m']
            if p['kind']=='plate':
                holes=p['holes_xy_m'];radius=p['hole_radius_m']
                if type(radius) not in (int,float) or not math.isfinite(radius) or radius<=0:
                    raise ValueError('positive plate hole radius required')
                if not holes or len(holes)>64 or any(len(h)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in h) for h in holes):
                    raise ValueError('finite plate hole coordinates required')
                if not np.allclose(np.sum(holes,axis=0),0.,atol=1e-12):raise ValueError('plate holes must balance about the plate centre')
                for i,h in enumerate(holes):
                    if any(abs(h[j])+radius>=dimensions[j]/2 for j in (0,1)) or any(math.dist(h,k)<=2*radius for k in holes[:i]):
                        raise ValueError('plate holes overlap or break an edge')
        else:
            if p['axis'] not in ('x', 'y', 'z'):raise ValueError('invalid cylinder axis')
            dimensions = [p['radius_m'], p['length_m']]
            if p['kind'] == 'tube':
                if not 0 < p['inner_radius_m'] < p['radius_m']:raise ValueError('invalid tube bore')
                dimensions.append(p['inner_radius_m'])
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in values + list(dimensions)):
            raise ValueError('finite reference geometry required')
        if any(v <= 0 for v in dimensions):raise ValueError('positive reference dimensions required')
    if len({p['id'] for p in spec['primitives']}) != len(spec['primitives']):
        raise ValueError('duplicate reference feature identity')
    return spec


def source(spec):
    validate_spec(spec)
    return PREFIX + json.dumps(spec, sort_keys=True, separators=(',', ':'), allow_nan=False)


def from_source(geometry):
    if geometry['kind'] != 'osr-parametric-reference':return None
    sources = geometry['source']
    if len(sources) != 1 or not isinstance(sources[0], str) or not sources[0].startswith(PREFIX):
        raise ValueError('embedded reference geometry specification required')
    return validate_spec(json.loads(sources[0][len(PREFIX):]))


def primitive_volume(p):
    validate_spec(dict(role='volume', primitives=[p]))
    if p['kind'] in ('box','plate'):
        volume=math.prod(p['dimensions_m'])
        if p['kind']=='plate':volume-=len(p['holes_xy_m'])*math.pi*p['hole_radius_m']**2*p['dimensions_m'][2]
        return volume
    return math.pi * (p['radius_m']**2 - p.get('inner_radius_m', 0.)**2) * p['length_m']


def primitive_inertia(p, mass):
    """Analytic uniform primitive inertia at its own CG, in local axes."""
    if p['kind'] in ('box','plate'):
        x, y, z = p['dimensions_m']
        gross_mass=mass if p['kind']=='box' else mass*math.prod(p['dimensions_m'])/primitive_volume(p)
        tensor=np.diag([gross_mass*(y*y+z*z)/12, gross_mass*(x*x+z*z)/12, gross_mass*(x*x+y*y)/12])
        if p['kind']=='plate':
            removed=mass*math.pi*p['hole_radius_m']**2*z/primitive_volume(p)
            for a,b in p['holes_xy_m']:
                d=np.array([a,b,0.]);r=p['hole_radius_m']
                tensor-=np.diag([removed*(3*r*r+z*z)/12]*2+[removed*r*r/2])+removed*((d@d)*np.eye(3)-np.outer(d,d))
        return tensor
    r2 = p['radius_m']**2 + p.get('inner_radius_m', 0.)**2
    axial = mass*r2/2; transverse = mass*(3*r2+p['length_m']**2)/12
    result = np.eye(3)*transverse
    result['xyz'.index(p['axis']), 'xyz'.index(p['axis'])] = axial
    return result


def aggregate(primitives, masses):
    if len(primitives) != len(masses) or not masses or any(type(m) not in (int,float) or not math.isfinite(m) or m <= 0 for m in masses):
        raise ValueError('one positive design mass per primitive required')
    validate_spec(dict(role='mass', primitives=primitives))
    total = sum(masses)
    cg = sum((m*np.asarray(p['centre_m']) for p,m in zip(primitives,masses)), np.zeros(3))/total
    inertia = np.zeros((3,3))
    for p,m in zip(primitives,masses):
        d = np.asarray(p['centre_m'])-cg
        inertia += primitive_inertia(p,m) + m*((d@d)*np.eye(3)-np.outer(d,d))
    return dict(mass_kg=total, cg_m=cg.tolist(), inertia_tensor_kg_m2=inertia.tolist())


def native_shape(spec, Part, App):
    validate_spec(spec);solids=[]
    for p in spec['primitives']:
        centre=App.Vector(*(v*1000 for v in p['centre_m']))
        if p['kind'] in ('box','plate'):
            x,y,z=[v*1000 for v in p['dimensions_m']]
            shape=Part.makeBox(x,y,z,centre-App.Vector(x/2,y/2,z/2))
            if p['kind']=='plate':
                for a,b in p['holes_xy_m']:
                    shape=shape.cut(Part.makeCylinder(p['hole_radius_m']*1000,z,centre+App.Vector(a*1000,b*1000,-z/2)))
        else:
            direction=App.Vector(*{'x':(1,0,0),'y':(0,1,0),'z':(0,0,1)}[p['axis']])
            length=p['length_m']*1000;base=centre-direction*(length/2)
            shape=Part.makeCylinder(p['radius_m']*1000,length,base,direction)
            if p['kind']=='tube':shape=shape.cut(Part.makeCylinder(p['inner_radius_m']*1000,length,base,direction))
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('invalid native reference solid')
        solids.append(shape)
    return Part.makeCompound(solids)
