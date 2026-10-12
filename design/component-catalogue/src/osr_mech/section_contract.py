"""Manufacturing sections shared by native CAD, meshes and analytical reductions.

SI units; supplied dimensions are design definitions, never measured acceptance.
"""
from __future__ import annotations
import math
from .engineering_definition import fingerprint, number


def rhs(width_m, height_m, wall_m, *, density_kg_m3):
    for key,value in [('width',width_m),('height',height_m),('wall',wall_m),('density',density_kg_m3)]:
        number(value,key,minimum=0)
        if value<=0:raise ValueError('section dimensions/density must be positive')
    if 2*wall_m>=min(width_m,height_m):raise ValueError('RHS wall closes the hollow section')
    wi=width_m-2*wall_m;hi=height_m-2*wall_m
    area=width_m*height_m-wi*hi
    # Local x is the member axis; y is width and z is section height.
    iy=(width_m*height_m**3-wi*hi**3)/12
    iz=(height_m*width_m**3-hi*wi**3)/12
    median_area=(width_m-wall_m)*(height_m-wall_m)
    torsion=4*median_area**2/(2*(width_m-wall_m)/wall_m+2*(height_m-wall_m)/wall_m)
    return dict(schema='osr-manufacturing-section/1',kind='rectangular-hollow',width_m=width_m,height_m=height_m,wall_m=wall_m,
        area_m2=area,iy_m4=iy,iz_m4=iz,j_torsion_m4=torsion,mass_kg_m=area*density_kg_m3,
        polar_area_moment_m4=iy+iz,torsion_basis='thin-wall closed-cell Bredt approximation; not polar inertia',
        corner_radius_m=0,corner_radius_basis='sharp-corner research section; rolled/welded radii require an explicit revision',
        density_kg_m3=density_kg_m3,physical_validation=False)


def geometry(section, length_m, *, centre_m=(0,0,0)):
    number(length_m,'member length',minimum=0)
    if length_m<=0:raise ValueError('member length must be positive')
    w,h,t=(section[k] for k in ('width_m','height_m','wall_m'))
    x,y,z=centre_m
    # Four disjoint manufactured walls; no overlapping corner mass.
    parts=[]
    for name,centre,dims in [
        ('top',[x,y,z+(h-t)/2],[length_m,w,t]),('bottom',[x,y,z-(h-t)/2],[length_m,w,t]),
        ('left',[x,y-(w-t)/2,z],[length_m,t,h-2*t]),('right',[x,y+(w-t)/2,z],[length_m,t,h-2*t])]:
        parts.append(dict(id=name,kind='box',centre_m=centre,dimensions_m=dims))
    return dict(role='manufactured RHS walls',primitives=parts)


def reconcile(section, length_m, geometry_spec):
    from .automated_geometry import aggregate, primitive_volume
    masses=[primitive_volume(p)*section['density_kg_m3'] for p in geometry_spec['primitives']]
    props=aggregate(geometry_spec['primitives'],masses)
    expected=section['mass_kg_m']*length_m
    if not math.isclose(props['mass_kg'],expected,rel_tol=1e-10):raise ValueError('manufacturing/analysis member mass mismatch')
    tensor=props['inertia_tensor_kg_m2'];density=section['density_kg_m3']
    for axis,key in [(1,'iy_m4'),(2,'iz_m4')]:
        reduced=(tensor[axis][axis]-expected*length_m**2/12)/(density*length_m)
        if not math.isclose(reduced,section[key],rel_tol=1e-9):raise ValueError('manufacturing/analysis bending inertia mismatch')
    return dict(section_sha256=fingerprint(section),geometry_sha256=fingerprint(geometry_spec),properties=props,
                analysis_mass_kg=expected,mass_reconciled=True,manufacturing_released=False)


def calculix_box(section, *, units='mm'):
    """CalculiX BOX: two outside dimensions and four wall thicknesses."""
    factor=1000 if units=='mm' else 1 if units=='m' else None
    if factor is None:raise ValueError('unsupported section units')
    w,h,t=(section[k]*factor for k in ('width_m','height_m','wall_m'))
    return f'{w:.12g},{h:.12g},{t:.12g},{t:.12g},{t:.12g},{t:.12g}'
