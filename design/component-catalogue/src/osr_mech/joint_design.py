"""Physical connection definitions and equilibrium-consistent local loads.

Unspecified manufacturing characteristics stay open; assembly solving cannot
substitute for preload, fits, procedures, material or tested joint laws.
"""
from __future__ import annotations
from copy import deepcopy
import numpy as np


FIELDS = {
    'bolted': ('hole_pattern_m', 'grip_stack_m', 'fastener_specification', 'clearance_m',
               'preload_range_n', 'locking', 'contact_surfaces', 'material_evidence'),
    'welded': ('section_thickness_m', 'weld_locations_m', 'weld_size_m', 'preparation',
               'parent_materials', 'procedure_reference', 'inspection_reference'),
    'bonded': ('layup', 'insert_geometry', 'bondline_thickness_m', 'surface_preparation',
               'interface_law', 'material_evidence', 'process_reference'),
    'bearing': ('seat_geometry', 'fit_specification', 'clearance_m', 'retention',
                'load_ratings', 'permitted_motion', 'supplier_evidence'),
    'suspension': ('installed_geometry', 'force_displacement_curves', 'damping_curves',
                   'preload', 'bump_stops', 'temperature_range_c', 'supplier_evidence'),
    'articulation': ('lower_bearing', 'drawbar', 'upper_links', 'anti_lift', 'stops',
                     'service_routing_limits', 'supplier_evidence'),
}


def definitions(model):
    from .engineering_definition import validate, fingerprint
    validate(model)
    rows = []
    for joint in model['joints']:
        kind = joint['type'] if joint['type'] in FIELDS else 'bearing'
        supplied = deepcopy(joint['definition'].get('physical', {}))
        row = dict(joint_id=joint['id'], revision=joint['revision'], kind=kind,
                   endpoints=deepcopy(joint['endpoints']),
                   fields={key: supplied.get(key) for key in FIELDS[kind]},
                   requirements=joint['requirements'], inspections=joint['inspections'])
        row['open_fields'] = [key for key, val in row['fields'].items() if val is None or val == [] or val == '']
        row['manufacturing_definition_complete'] = not row['open_fields']
        row['production_released'] = False
        rows.append(row)
    return dict(schema='osr-physical-joint-register/1', configuration_sha256=fingerprint(model),
                joints=rows, production_released=False)


def bolt_group(points_m, force_moment_si, *, preload_range_n=None, friction=None, tensile_area_m2=None):
    """Equal axial/shear stiffness screening; no prying or code resistance claim."""
    points=np.asarray(points_m,dtype=float);demand=np.asarray(force_moment_si,dtype=float)
    if points.ndim!=2 or points.shape[1]!=3 or len(points)<3 or demand.shape!=(6,):
        raise ValueError('three or more bolt locations and six joint resultants required')
    if not np.isfinite(points).all() or not np.isfinite(demand).all():raise ValueError('finite joint geometry/load required')
    centre=points.mean(axis=0);B=np.zeros((6,3*len(points)))
    for i,(x,y,z) in enumerate(points-centre):
        B[:3,3*i:3*i+3]=np.eye(3)
        B[3:,3*i:3*i+3]=[[0.,-z,y],[z,0.,-x],[-y,x,0.]]
    if np.linalg.matrix_rank(B)<6:raise ValueError('bolt pattern cannot resolve all joint moments')
    loads=(B.T@np.linalg.solve(B@B.T,demand)).reshape(-1,3)
    if preload_range_n is not None:
        lo,hi=preload_range_n
        if not all(np.isfinite([lo,hi])) or not 0<=lo<=hi:raise ValueError('invalid bolt preload bounds')
    if friction is not None and (not np.isfinite(friction) or friction<0):raise ValueError('invalid joint friction')
    if tensile_area_m2 is not None and (not np.isfinite(tensile_area_m2) or tensile_area_m2<=0):raise ValueError('invalid tensile area')
    rows=[]
    for point,load in zip(points,loads):
        shear=float(np.linalg.norm(load[:2]));tension=max(float(load[2]),0.)
        clamp=None if preload_range_n is None else max(0.,preload_range_n[0]-tension)
        rows.append(dict(position_m=point.tolist(),force_n=load.tolist(),shear_n=shear,external_tension_n=tension,
            minimum_clamp_n=clamp,slip_margin_n=None if clamp is None or friction is None else friction*clamp-shear,
            external_tensile_stress_pa=None if tensile_area_m2 is None else tension/tensile_area_m2))
    return dict(schema='osr-bolt-group-screening/1',bolts=rows,
        equilibrium_residual=float(np.linalg.norm(B@loads.ravel()-demand)),
        strength_accepted=False,engineering_released=False,
        assumptions=['equal axial/shear stiffness', 'resultants expressed at pattern centroid',
                     'plate prying and contact redistribution require native submodel'])
