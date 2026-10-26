from copy import deepcopy
import math
from pathlib import Path
import pytest

from engineering.comfort_design import ROOT
from engineering.comfort_design import vehicle as v

EVIDENCE_ROOT=next(p for p in (ROOT,*ROOT.parents) if (p/'docs/design-engine/halbach-scaling/comparison.json').is_file())


@pytest.fixture(scope='module')
def car():return v.build(EVIDENCE_ROOT)


def test_exact_replacements_preserve_unlocated_interior_and_remaining_account(car):
    m=car['mass']
    assert m['accounted_tare_kg_per_car']==pytest.approx(17356.683728076856)
    assert m['accounted_cap_loaded_kg_per_car']==pytest.approx(20806.683728076856)
    assert m['accounted_160_control_kg_per_car']==pytest.approx(29356.683728076856)
    assert abs(m['replacement_residual_kg'])<1e-6
    assert m['remaining_noninterior_allocation_kg']==pytest.approx(4778.253763406856)
    assert m['counted_seat_stock_kg']+m['unlocated_interior_remainder_kg']==pytest.approx(800.)
    assert m['installed_tare_kg_per_car'] is None
    assert m['CG_m'] is None and m['inertia_kg_m2'] is None
    assert math.fsum(r['mass_kg'] for r in car['inventory'])==pytest.approx(m['accounted_tare_kg_per_car'])


def test_four_post_omissions_require_single_seat_derivatives(car):
    units=car['physical_definition']['body']['seat_units']
    assert sum(u['places'] for u in units)==44
    assert sum(u['places']==2 for u in units)==20
    assert sum(u['places']==1 for u in units)==4
    assert car['components']['single_seat']['necessary_screen']=='pass'
    assert car['components']['single_seat']['fixtures']['total_deflection_m']<.005
    assert car['mass']['counted_seat_stock_kg']!=pytest.approx(22*car['components']['paired_seat']['counted_mass_kg'])
    assert len({pid for u in units for pid in u['place_ids']})==44


def test_failed_crossrail_fit_is_retained_and_revision_checks_lower_material_bounds(car):
    roof=car['components']['roof_revision'];chosen=roof['selected']
    assert roof['rejected_crossrail']['matched_assembly_screen']=='fail'
    assert roof['rejected_crossrail']['total_common_volume_m3']>0
    assert len(roof['variants'])==4
    assert [p['necessary_screen'] for p in roof['variants']]==['fail','fail','pass','pass']
    assert chosen['physical_definition']['skin_each_m']==.0012
    assert chosen['physical_definition']['core_m']==.045
    assert chosen['physical_definition']['extra_crossrails']==0
    assert roof['selected_minimum_rail_clearance_m']>0
    assert all(f['minimum_skin_m']==pytest.approx(.00116) for f in chosen['fixtures'])
    assert all(f['minimum_core_m']==pytest.approx(.0445) for f in chosen['fixtures'])
    assert car['interfaces']['roof_top_z_m']==pytest.approx(2.8054)


def test_native_material_subset_never_assigns_unknown_allowances_a_solid(car):
    ids={p['id'] for p in car['geometry_parts']}
    assert len(ids)==len(car['geometry_parts'])
    assert not any('unlocated' in name or 'allocation' in name for name in ids)
    assert car['located_material_properties']['mass_kg']<car['mass']['accounted_tare_kg_per_car']
    assert len(car['interfaces']['HVAC_packages'])==5
    assert all(p['geometry_is_material'] is False for p in car['interfaces']['HVAC_packages'])
    assert not any(name.startswith('HVAC') for name in ids)
    assert all(p['mass_kg']>0 for p in car['geometry_parts'])
    assert all(p['complete_installed_inventory'] is False for p in car['coverage'])


def test_geometry_owns_twenty_four_modules_and_exact_door_voids(car):
    mounts=car['interfaces']['magnetic_mounts'];assert len(mounts)==24
    assert sorted(set(m['translation_m'][1] for m in mounts))==[-.88,.88]
    assert all(m['translation_m'][2]==-1.16 for m in mounts)
    assert all(m['reference_gap_m']==.012 for m in mounts)
    assert len(car['interfaces']['door_openings'])==2
    opaque=[p for p in car['geometry_parts'] if p['id'].startswith('door/') and '/core/' in p['id']]
    assert sum(p['volume_m3'] for p in opaque)==pytest.approx(4*(.7*2.1-.5)*.060)
    glazing=[p for p in car['geometry_parts'] if p['id'].endswith('PVB')]
    assert sum(p['volume_m3'] for p in glazing)==pytest.approx(26*.00076)


def test_identity_and_validation_reject_forged_installed_mass(car,monkeypatch):
    changed=deepcopy(car);changed['mass']['installed_tare_kg_per_car']=0
    monkeypatch.setattr(v,'build',lambda root:car)
    with pytest.raises(ValueError,match='differs'):v.validate(changed,EVIDENCE_ROOT)
    assert car['candidate_id']!=car['body_candidate_id']
    assert not car['configuration_adopted'] and not car['physical_accepted']
    assert car['readiness']['physical_acceptance']=='hold'


def test_geometry_properties_of_a_real_drilled_panel():
    p=v._primitive('drilled',[1.,2.,.06],[3.,4.,5.],80.,holes=[dict(axis='z',diameter_m=.02,x_m=.2,y_m=.2)])
    assert p['volume_m3']==pytest.approx(.12-math.pi*.01**2*.06)
    assert p['mass_kg']==pytest.approx(80*p['volume_m3'])
    assert p['cg_m'][0]>3.5 and p['cg_m'][1]>5.
