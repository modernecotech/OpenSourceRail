"""Same-candidate physical propagation does not inherit reference acceptance."""
from copy import deepcopy
import pytest
from engineering.reference_cell import bundle,vehicles,physics
from engineering.design_search import railway_bundle,system_motion
from engineering.component_registry import make_registry
from engineering.station_rail.common import identity

@pytest.fixture(scope='module')
def fleet():return [vehicles.evaluate(name) for name in vehicles.variants()]

@pytest.fixture(scope='module')
def composed(fleet):return [bundle.materialize(v) for v in fleet]


def test_all_five_equipped_bodies_reach_canonical_motion_interfaces(fleet,composed):
    assert len({b['candidate_id'] for b in composed})==5
    for v,b in zip(fleet,composed):
        assert railway_bundle.validate(b)==b and system_motion._bundle(b)==b
        assert b['body_candidate_id']==v['candidate_id']
        assert b['mass']['accounted_tare_kg_per_car']==pytest.approx(v['summary']['mass_upper_bound_kg']/6)
        assert b['mass']['accounted_cap_loaded_kg_per_car']-b['mass']['accounted_tare_kg_per_car']==pytest.approx(3450.)
        assert b['mass']['accounted_160_control_kg_per_car']-b['mass']['accounted_tare_kg_per_car']==pytest.approx(12000.)
        assert b['retained_equipment_accounts']==[] and b['complete_installed_mass_kg'] is None
        assert b['motor_definition']['segmented_secondary_field_model_supported'] is False
        assert b['available_force_map'] is None
        assert physics.evaluate(b)['execution']=='not-run'


def test_new_rotor_and_brake_definitions_use_actual_parts_not_reference(composed):
    for b in composed:
        r=b['brake_definition']['rotors']
        assert r['radius_m']==.32 and len(r['parts'])==28
        assert len(r['unresolved_rotating_equipment'])==8
        assert all(v['I_axial_kg_m2'] is None for v in r['unresolved_rotating_equipment'])
        assert b['rotating_equivalent_kg_per_car']==pytest.approx(sum(v['I_axial_kg_m2'] for v in r['parts'])/.32**2)
        assert b['brake_definition']['pad_outer_radius_m']==.21
        assert b['brake_definition']['pad_inner_radius_m']==.08
        assert b['brake_definition']['supplier_friction_or_fade_curve'] is None
        assert b['brake_definition']['candidate_id']==b['candidate_id']
        assert b['brake_definition']['support_component_id']==b['support_component_id']
        assert all('/' in v['occurrence_id'] for v in r['parts'])


def test_segmented_fin_and_primary_alignment_are_new_explicit_physics(composed):
    b=composed[0];p=b['motor_definition']['physical_configuration']
    assert p['secondary_segment_count']==3 and p['secondary_length_m']==2.98
    assert p['secondary_thickness_m']==.012 and p['secondary_height_m']==.30
    assert p['secondary_bottom_TOR_m']==pytest.approx(.36)
    assert len(b['wayside_primary_stock'])==486
    assert all(v['motor_component_id']==b['propulsion_component_id'] for v in b['wayside_primary_stock'])
    assert min(v['at_m'][2] for v in b['wayside_primary_stock'])>=.36-1e-9
    assert b['motor_definition']['bare_primary_stock_kg_per_bank']==pytest.approx(sum(v['mass_kg'] for v in b['wayside_primary_stock']))
    from engineering.railway_completion import motor
    with pytest.raises(ValueError):motor.request(b)


def test_route_and_architecture_changes_do_not_reuse_candidate_identity(fleet,composed):
    a=composed[0];b=bundle.materialize(fleet[0],1500.);c=bundle.materialize(fleet[0],propulsion='six-20m');d=bundle.materialize(fleet[0],guideway='twin')
    assert len({v['candidate_id'] for v in (a,b,c,d)})==4
    assert {v['body_candidate_id'] for v in (a,b,c,d)}=={a['body_candidate_id']}
    assert b['architecture_case']['physical_definition']['route']['station_spacing_m']==1500.
    assert len(c['architecture_case']['physical_definition']['wayside']['bank_starts_from_initial_nose_m'])==6


def test_vehicle_bytes_are_not_mutated_by_cell_adaptation(fleet):
    v=fleet[0];before=deepcopy(v);bundle.materialize(v)
    assert v==before


def test_resealed_derived_vehicle_summary_does_not_replace_registry_mass(fleet):
    v=deepcopy(fleet[0]);v['train_mass_properties']['mass_upper_bound_kg']=1.
    v['evaluation_id']=identity({k:x for k,x in v.items() if k!='evaluation_id'})
    b=bundle.materialize(v)
    assert b['mass']['accounted_tare_kg_per_car']==pytest.approx(v['summary']['mass_upper_bound_kg']/6)


def test_mass_only_registry_revision_changes_evaluation_not_physical_candidate(fleet,composed):
    v=deepcopy(fleet[0]);r=v['registry'];part=next(p for p in r['parts'] if p['geometry']['kind']=='envelope')
    part['mass']['upper_bound_kg']+=1.
    part['revision_id']=identity({k:x for k,x in part.items() if k!='revision_id'})
    # Rebuild occurrence links via the canonical registry constructor; physical
    # definition remains the same while property/revision identity changes.
    for o in r['occurrences']:
        if o['part_definition_id']==part['physical_definition_id']:o['part_revision_id']=part['revision_id']
    r['registry_id']=identity({k:x for k,x in r.items() if k!='registry_id'})
    v['evaluation_id']=identity({k:x for k,x in v.items() if k!='evaluation_id'})
    b=bundle.materialize(v)
    assert b['candidate_id']==composed[0]['candidate_id']
    assert b['definition_id']!=composed[0]['definition_id']
    assert b['mass']['accounted_tare_kg_per_car']>composed[0]['mass']['accounted_tare_kg_per_car']


def test_registry_frame_is_explicitly_mapped_to_front_displacement_route_frame(composed):
    b=composed[0];v=b['physical_definition']['vehicle']
    assert v['train_local_to_route_at_front_zero']==[[1.,0.,0.,-104.5],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
    assert len(b['route_axle_offsets_from_leading_nose_m'])==24
    assert all(r['offset_behind_leading_nose_m']==pytest.approx(104.5-r['train_local_transform'][0][3]) for r in b['route_axle_offsets_from_leading_nose_m'])
    leading=[r for r in b['route_secondary_segments_at_front_zero_m'] if r['occurrence_id'].startswith('car-6/')]
    assert len(leading)==3
    assert sorted(r['transform_at_leading_front_zero'][0][3] for r in leading)==pytest.approx([-13.,-10.,-7.])
    assert b['architecture_case']['physical_definition']['wayside']['bank_starts_from_initial_nose_m'][0]==-13.


@pytest.mark.parametrize('layout',['longer-distributed','continuous-500m','station-cable','auxiliary-rescue'])
def test_unowned_motor_families_do_not_reuse_twenty_metre_LIM_hardware(fleet,layout):
    with pytest.raises(ValueError,match='no owned complete motor adapter'):bundle.materialize(fleet[0],propulsion=layout)
