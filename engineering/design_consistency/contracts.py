"""Shared definitions for complete research assemblies and their representations."""
from copy import deepcopy
import math
from pathlib import Path
from osr_mech.engineering_definition import fingerprint, number, evidence
from osr_mech.automated_geometry import validate_spec, aggregate, primitive_volume
from osr_mech.section_contract import rhs, geometry, reconcile

ROOT=Path(__file__).resolve().parents[2]


def validate(contract):
    if contract.get('schema')!='osr-engineering-representations/1' or not contract.get('revision'):
        raise ValueError('versioned engineering representation contract required')
    if any(contract.get(k) is not False for k in ('physical_validation','production_released')):
        raise ValueError('research contract cannot grant physical/manufacturing release')
    ids=set();materials=contract['materials']
    for row in contract['parts']:
        if not row.get('id') or row['id'] in ids:raise ValueError('unique physical part identity required')
        ids.add(row['id'])
        if row['material'] not in materials:raise ValueError('unknown material region')
        density=number(materials[row['material']]['density_kg_m3'],'material density',minimum=0)
        if density<=0:raise ValueError('positive material density required')
        validate_spec(row['manufacturing'])
        if 'laminate_ply'in row:
            ply=row['laminate_ply'];number(ply['angle_deg'],'ply orientation')
            for primitive in row['manufacturing']['primitives']:
                thickness=primitive['z_upper_m']-primitive['z_lower_m']if primitive['kind']=='curved-layer'else primitive['dimensions_m'][2]
                if not math.isclose(thickness,ply['thickness_m'],rel_tol=1e-9):raise ValueError('ply schedule does not match manufactured thickness')
        for key in ('datums','joints','loads','manufacturing_limits','inspection_characteristics','evidence'):
            if key not in row:raise ValueError('missing physical contract field: '+key)
        for ref in row['evidence']:evidence(ref,ROOT)
        if row['analysis']['physical_part_id']!=row['id'] or row['coordination']['physical_part_id']!=row['id']:
            raise ValueError('representation identity mismatch')
        props=aggregate(row['manufacturing']['primitives'],[primitive_volume(p)*density for p in row['manufacturing']['primitives']])
        from osr_mech.engineering_definition import _transform
        _transform(row['placement'])
        import numpy as np
        rotation=np.asarray(row['placement']['rotation']);cg=rotation@np.asarray(props['cg_m'])+row['placement']['translation_m']
        inertia=rotation@np.asarray(props['inertia_tensor_kg_m2'])@rotation.T
        for representation in (row['analysis'],row['properties']):
            if not math.isclose(representation['mass_kg'],props['mass_kg'],rel_tol=1e-9):raise ValueError('CAD/analysis mass differs')
            if not np.allclose(representation['cg_m'],cg,rtol=1e-9,atol=1e-10):raise ValueError('CAD/analysis datum differs')
            if not np.allclose(representation['inertia_tensor_kg_m2'],inertia,rtol=1e-9,atol=1e-10):raise ValueError('CAD/analysis inertia differs')
        section=row['analysis']['section']
        if section:
            expected=rhs(section['width_m'],section['height_m'],section['wall_m'],density_kg_m3=density)
            if fingerprint(section)!=fingerprint(expected):raise ValueError('section properties do not follow dimensions/material')
        if row.get('production_released') is not False:raise ValueError('part has no manufacturing release')
        if row['analysis']['geometry_sha256']!=fingerprint(row['manufacturing']):raise ValueError('analysis refers to stale manufactured geometry')
        if row['coordination']['geometry_sha256']!=fingerprint(row['manufacturing']):raise ValueError('coordination refers to stale manufactured geometry')
    for joint in contract.get('assembly_joints',[]):
        for group in joint.get('instance_groups',[]):
            if not set(group['physical_part_ids'])<=ids:raise ValueError('joint instance refers to an unknown physical part')
    for stage in contract.get('construction_stages',[]):
        if not set(stage['parts'])<=ids or not stage.get('supports') or not stage.get('loads'):
            raise ValueError('construction stage requires explicit parts, supports and loads')
    return contract


def part(identity,material,spec,materials, *, section=None,joints=(),loads=(),limits=None,inspections=(),datums=None,placement=None):
    density=materials[material]['density_kg_m3']
    props=aggregate(spec['primitives'],[primitive_volume(p)*density for p in spec['primitives']])
    import numpy as np
    placement=placement or {'translation_m':[0,0,0],'rotation':np.eye(3).tolist()}
    from osr_mech.engineering_definition import _transform
    _transform(placement)
    rotation=np.asarray(placement['rotation']);props['cg_m']=(rotation@np.asarray(props['cg_m'])+placement['translation_m']).tolist()
    props['inertia_tensor_kg_m2']=(rotation@np.asarray(props['inertia_tensor_kg_m2'])@rotation.T).tolist()
    return dict(id=identity,placement=placement,revision='RESEARCH-1',material=material,manufacturing=spec,datums=datums or {'origin_m':[0,0,0]},
        joints=list(joints),loads=list(loads),manufacturing_limits=limits or {'minimum_wall_m':None,'tolerance_m':None},
        inspection_characteristics=list(inspections),evidence=[],
        analysis=dict(physical_part_id=identity,geometry_sha256=fingerprint(spec),mass_kg=props['mass_kg'],
            cg_m=props['cg_m'],inertia_tensor_kg_m2=props['inertia_tensor_kg_m2'],section=section,representation='section/solid'),
        coordination=dict(physical_part_id=identity,geometry_sha256=fingerprint(spec),simplification='same physical primitives'),
        properties=props,production_released=False)


def box(identity,length,width,height,centre):
    return dict(id=identity,kind='box',centre_m=list(centre),dimensions_m=[length,width,height])


def member(identity,length,width,height,wall,material,materials,centre=(0,0,0),**kwargs):
    section=rhs(width,height,wall,density_kg_m3=materials[material]['density_kg_m3'])
    spec=geometry(section,length,centre_m=centre);reconcile(section,length,spec)
    return part(identity,material,spec,materials,section=section,**kwargs)


def summary(contract):
    validate(contract)
    regions=[p for p in contract['parts']]
    total=sum(p['properties']['mass_kg'] for p in regions)
    cg=[sum(p['properties']['mass_kg']*p['properties']['cg_m'][i]for p in regions)/total for i in range(3)]
    import numpy as np
    inertia=np.zeros((3,3))
    for p in regions:
        delta=np.asarray(p['properties']['cg_m'])-cg;mass=p['properties']['mass_kg']
        inertia+=np.asarray(p['properties']['inertia_tensor_kg_m2'])+mass*((delta@delta)*np.eye(3)-np.outer(delta,delta))
    return dict(schema='osr-representation-correspondence/1',configuration_sha256=fingerprint(contract),
        part_count=len(regions),mass_kg=total,cg_m=cg,inertia_tensor_kg_m2=inertia.tolist(),
        every_defined_part_mapped=True,mass_cg_inertia_reconciled=True,
        unresolved_part_allocations=contract.get('unresolved_part_allocations',[]),complete_installed_kit=False,
        local_section_stiffness_qualified=False,
        open_evidence=contract['mandatory_evidence'],physical_validation=False,production_released=False)
