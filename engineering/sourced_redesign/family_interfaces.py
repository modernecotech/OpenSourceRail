"""Geometry-first cassette/rib fit repair before the frozen bond/cap generator.

A lower rib is a physical revision. Full stock sections are retained; a source
hypothesis of4mm minimum metal cap plus two0.6mm bonds is not a strength limit.
Unchanged families return the exact input object to preserve native bindings.
"""
from copy import deepcopy
from pathlib import Path
import numpy as np
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest
from engineering.component_registry import make_registry,summary
from engineering.reference_cell.vehicles import _mass_properties
from engineering.sourced_case import layered_structure as layer

PRODUCER='engineering/sourced_redesign/family_interfaces.py'
FLAGS=layer.FLAGS


def diagnose(vehicle,*,bond_thickness_m=.0006,minimum_cap_m=.004):
    layer._vehicle(vehicle)
    if not .0003<=bond_thickness_m<=.0012 or not .002<=minimum_cap_m<=.010:raise ValueError('Explicit bounded physical bond/cap hypotheses required')
    rows,panels=layer.inventory(vehicle);requests=[]
    for p in panels:
        for patch in p['bearing_patches']:
            original=patch['actual_vertical_gap_m'];after_skin=original-bond_thickness_m;target=minimum_cap_m+2*bond_thickness_m
            requests.append(dict(panel_id=p['panel_id'],rib_occurrence_id=patch['source_occurrence_id'],kind=p['kind'],
                original_gap_m=original,after_skin_bond_separation_gap_m=after_skin,minimum_stack_m=target,
                required_rib_lowering_m=max(0.,target-after_skin),actual_interference_m=max(0.,-after_skin)))
    if any(q['kind']=='floor' and q['required_rib_lowering_m']>1e-9 for q in requests):raise ValueError('Floor load path needs a separate physical repair; no roof-only adaptation can conceal it')
    move=max((q['required_rib_lowering_m'] for q in requests if q['kind']=='roof'),default=0.)
    if move>.015:raise ValueError('More than15mm roof-rib relocation requires a wider body/interior architecture revision')
    value=dict(schema='osr-family-interface-fit/1',candidate_id=vehicle['candidate_id'],vehicle_evaluation_id=vehicle['evaluation_id'],
        bond_thickness_m=bond_thickness_m,minimum_cap_m=minimum_cap_m,roof_rib_lowering_m=move,
        adaptation_needed=move>1e-9,requests=requests,
        limitation='Finite stock fit only; rib/load-path, headroom, equipment, access and fire/structural qualification remain open',**FLAGS)
    value['review_id']=identity(value);return value


def revision(vehicle,*,root=ROOT,bond_thickness_m=.0006,minimum_cap_m=.004):
    review=diagnose(vehicle,bond_thickness_m=bond_thickness_m,minimum_cap_m=minimum_cap_m)
    if not review['adaptation_needed']:return vehicle
    move=review['roof_rib_lowering_m'];rows=layer._rows(vehicle);roofids={r['occurrence']['occurrence_id'].split('/',1)[1] for r in rows if layer._is(r,'roof-transverse-rib')}
    if not roofids:raise ValueError('Actual roof rib occurrences required')
    occ=deepcopy(vehicle['registry']['occurrences'])
    for o in occ:
        if o['occurrence_id'].split('/',1)[1] in roofids:o['transform'][2][3]-=move
    registry=make_registry(vehicle['label']+'; corrected finite roof interface fit',vehicle['registry']['parts'],occ,vehicle['functional_requirements'],
        parent_candidate_id=vehicle['candidate_id'],assemblies=vehicle['registry']['assemblies'],materials=vehicle['registry']['materials'])
    result=deepcopy(vehicle);result.pop('evaluation_id');result.update(candidate_id=registry['candidate_id'],registry=registry,summary=summary(registry),label=vehicle['label']+'; corrected finite roof interface fit')
    parts={p['physical_definition_id']:p for p in registry['parts']};massrows=[]
    for o in registry['occurrences']:
        T=np.asarray(o['transform']);axis='x' if abs(T[0,2])>.9 else 'y' if abs(T[1,2])>.9 else 'z'
        massrows.append(dict(part=parts[o['part_definition_id']],xyz=T[:3,3].tolist(),axis=axis,car=o['occurrence_id'].split('/')[0]))
    result['per_car_mass_properties']=_mass_properties([r for r in massrows if r['car']=='car-1']);result['train_mass_properties']=_mass_properties(massrows)
    source=layer.sources(vehicle,root);source[PRODUCER]=digest(Path(root)/PRODUCER);source['engineering/sourced_redesign/__init__.py']=digest(Path(root)/'engineering/sourced_redesign/__init__.py')
    if source[PRODUCER]!=digest(__file__):raise ValueError('Executing family adapter differs from declared source root')
    result['source_sha256']=dict(sorted(source.items()));result['family_interface_revision']=dict(parent_candidate_id=vehicle['candidate_id'],parent_vehicle_evaluation_id=vehicle['evaluation_id'],
        input_fit_review=review,lowering_m=move,moved_roof_ribs_per_car=len(roofids),part_geometry_or_material_changed=False,
        rigid_transform_changed=True,manufactured_section_preserved=True,stock_mass_change_kg=0.,
        displacement_direction=[0.,0.,-1.],reason='Remove true face/rib interference and leave a positive counted bond/cap stack',
        headroom_and_equipment_sweeps_qualified=False,actual_laminate_or_joint_strength_qualified=False,
        remaining_tasks=['Regenerate counted adhesive/cap geometry from this candidate','Regenerate matching whole-body bracket geometry',
            'Check lowered-rib equipment/service/tool/suspension envelopes','Evaluate structure with exact new mass/CG and load paths'])
    result['evaluation_id']=identity(result);layer._vehicle(result)
    check=diagnose(result,bond_thickness_m=bond_thickness_m,minimum_cap_m=minimum_cap_m)
    if check['adaptation_needed']:raise ValueError('Revised physical roof interfaces still violate declared positive stock stack')
    return result
