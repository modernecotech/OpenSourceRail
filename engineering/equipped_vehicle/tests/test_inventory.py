"""Mass provenance and full-tensor regression tests for the equipped ledger."""
from copy import deepcopy
import math
from pathlib import Path
import os

import numpy as np
import pytest

from engineering.research_test_support import evidence_root
from engineering.equipped_vehicle import ROOT,FLAGS
from engineering.equipped_vehicle.inventory import combine,build_inventory,validate_inventory,gfrp_design_space,SYSTEMS
from engineering.halbach_scaling import candidates,vehicles

EVIDENCE = evidence_root(Path(__file__).resolve().parents[3],
    required=('docs/design-engine/halbach-scaling/comparison.json',),
    sources=('engineering/equipped_vehicle/inventory.py',))


@pytest.fixture(scope='module')
def candidate():
    body=next(b for b in vehicles.variants(EVIDENCE) if b['name'].startswith('6082-six-cell-deep-40kn/'))
    magnetic=next(m for m in candidates.candidates(EVIDENCE) if m['recipe_id']=='HS-V012-W40-H8-P1-Y00-D')
    return body,magnetic


@pytest.fixture(scope='module')
def equipped(candidate):return build_inventory(*candidate,root=EVIDENCE)


def test_products_of_inertia_and_translation_do_not_disappear():
    regions=[dict(id='a',mass_kg=1.,cg_m=[1.,1.,0.],inertia_kg_m2=np.diag([1.,2.,3.]).tolist()),
             dict(id='b',mass_kg=1.,cg_m=[-1.,-1.,0.],inertia_kg_m2=np.diag([1.,2.,3.]).tolist())]
    r=combine(regions)
    assert r['mass_kg']==2 and r['cg_m']==[0,0,0]
    assert np.asarray(r['inertia_kg_m2'])==pytest.approx(np.asarray([[4.,-2.,0.],[-2.,6.,0.],[0.,0.,10.]]))
    for p in regions:p['cg_m']=(np.asarray(p['cg_m'])+[3,4,5]).tolist()
    moved=combine(regions)
    assert moved['cg_m']==[3,4,5]
    assert np.asarray(moved['inertia_kg_m2'])==pytest.approx(np.asarray(r['inertia_kg_m2']))


@pytest.mark.parametrize('bad',[None,True,'1',0.,-1.,float('nan')])
def test_unknown_or_nonphysical_mass_cannot_be_located_as_zero(bad):
    with pytest.raises((ValueError,TypeError)):
        combine([dict(id='a',mass_kg=bad,cg_m=[0,0,0],inertia_kg_m2=np.eye(3).tolist())])


def test_noncentral_or_missing_tensor_is_rejected():
    row=dict(id='a',mass_kg=1.,cg_m=[0,0,0],inertia_kg_m2=[[1,2,0],[0,1,0],[0,0,1]])
    with pytest.raises(ValueError):combine([row])
    row['inertia_kg_m2']=None
    with pytest.raises(ValueError):combine([row])
    row['inertia_kg_m2']=np.diag([1.,1.,3.]).tolist()
    with pytest.raises(ValueError):combine([row])


def test_exact_composition_mass_closes_without_claiming_full_installed_properties(equipped,candidate):
    composed=vehicles.compose(*candidate,root=EVIDENCE)
    assert equipped['composition_id']==composed['candidate_id']
    assert equipped['body_candidate_id']==candidate[0]['candidate_id']
    assert equipped['magnet_component_id']==candidate[1]['physical_id']
    assert equipped['comparison_empty_kg_per_car']==pytest.approx(composed['comparison_empty_kg_per_car'])
    assert math.fsum(r['mass_kg'] for r in equipped['occurrences'])==pytest.approx(composed['comparison_empty_kg_per_car'])
    assert equipped['comparison_aw3_kg_per_car']-equipped['comparison_empty_kg_per_car']==12000.
    assert equipped['installed_empty_kg_per_car'] is equipped['cg_m'] is equipped['inertia_kg_m2'] is equipped['modal_model'] is None
    assert all(equipped[k] is False for k in FLAGS)
    assert 0<equipped['located_share_of_accounted_comparison']<.5


def test_removed_frame_is_not_retained_and_magmodule_local_pose_is_not_car_pose(equipped,candidate):
    removed=set(candidate[0]['frame']['removed_stock_ids'])
    assert not ({'retained/'+name for name in removed}&{r['id'] for r in equipped['occurrences']})
    modules=[r for r in equipped['occurrences'] if r['id'].startswith('module/')]
    assert modules and all(r['geometry'] is None and r['local_geometry']['group']=='train' for r in modules)
    assert math.fsum(r['mass_kg'] for r in modules)==pytest.approx(24*candidate[1]['stock']['train_known_mass_kg_per_module'])
    assert len({r['id'] for r in equipped['occurrences']})==len(equipped['occurrences'])


def test_allocation_and_supplier_references_are_not_turned_into_solid_geometry(equipped):
    rows=equipped['occurrences']
    unlocated=[r for r in rows if r['evidence_class'] in ('supplier-reference','unlocated-allocation','located-envelope-allocation')]
    assert all(r['geometry'] is None for r in unlocated)
    assert equipped['accounted_mass_by_evidence_class_kg']['supplier-reference']==1124.
    assert equipped['accounted_mass_by_evidence_class_kg']['unlocated-allocation']==pytest.approx(5578.253763406856)
    assert set(r['system'] for r in equipped['missing_inventory'])==set(SYSTEMS)
    assert all(r['mass_kg'] is None for r in equipped['missing_inventory'])


def test_every_material_or_reference_occurrence_has_assembly_and_structural_contract(equipped):
    for row in [*equipped['occurrences'],*equipped['missing_inventory']]:
        structural=row['structural_participation'];assembly=row['assembly_function']
        assert structural['credited_in_global_model'] is False
        assert structural['demonstrated'] in (None,False)
        assert all(assembly[k] for k in ('insertion','test','removal','repair'))
        assert assembly['insertion_path_verified'] is assembly['removal_path_verified'] is False


def test_tampered_or_mixed_selected_candidate_cannot_supply_an_equipped_distribution(equipped,candidate):
    altered=deepcopy(equipped);altered['cg_m']=[0,0,0];altered['complete_equipped_vehicle']=True
    with pytest.raises(ValueError,match='differs'):validate_inventory(altered,*candidate,root=EVIDENCE)
    body=deepcopy(candidate[0]);body['frame']['counted_material_mass_kg']-=100
    with pytest.raises(ValueError):build_inventory(body,candidate[1],root=EVIDENCE)


def test_gfrp_seed_and_design_variables_cannot_become_selected_halbach_body():
    seed=gfrp_design_space()
    assert len(seed['seed_geometry_id'])==64
    assert seed['compatible_with_selected_halbach_composition'] is False
    assert seed['selected_composition_id'] is None and seed['sampled_candidates']==[]
    assert seed['complete_installed_mass_kg'] is seed['modal_model'] is None
