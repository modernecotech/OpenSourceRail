"""Proposed door header geometry has distinct children and explicit holds."""
from math import pi

import pytest

from engineering.station_rail.common import identity
from engineering.vehicle_parts import door_research_child as child
from tools.automation import v07_door_route as route


def test_parametric_children_have_ancestry_and_no_selection():
    family=child.evaluate_family()
    assert family['family_id']==identity({k:v for k,v in family.items() if k!='family_id'})
    assert family['parent_physical_candidate_id']==route.PHYSICAL_CHILD
    assert family['selected_candidate_id'] is None
    assert len({r['physical_candidate_id'] for r in family['rows']})==3
    for row in family['rows']:
        definition=row['physical_definition']
        assert row['physical_candidate_id']==identity(definition)
        assert row['evaluation_id']==identity({k:v for k,v in row.items() if k!='evaluation_id'})
        assert row['physical_candidate_id']!=route.PHYSICAL_CHILD
        assert definition['parent_physical_candidate_id']==route.PHYSICAL_CHILD
        assert definition['parent_installed_candidate_id']==route.INSTALLED_CHILD
        assert len(definition['part_definitions'])==74
        assert sum(definition['parts_per_opening'].values())==694
        assert row['selection_id'] is None and row['candidate_adopted'] is False
        assert row['parent_installed_child_relabelled'] is False
        assert row['ready_for_native_assembly'] is False
        assert row['engineering_accepted'] is False and row['physical_accepted'] is False


def test_two_pulley_ideal_pitch_bound_and_discretization_are_explicit():
    row=child.evaluate_radius(.03)
    b=row['necessary_bounds'];definition=row['physical_definition']
    assert row['disposition']=='held-research-geometry'
    assert b['ideal_centre_distance_m']==pytest.approx((5.8-2*pi*.03)/2)
    assert b['ideal_pitch_length_residual_m']==pytest.approx(0,abs=1e-12)
    assert b['projected_pulley_span_m']<b['header_stock_length_m']==3.
    assert b['guide_header_arithmetic_margin_m']==pytest.approx(.1)
    assert b['guide_motion_arithmetic_margin_m']==pytest.approx(.06)
    assert b['pitch_equals_cut_length_unverified'] is True
    assert row['sampled_belt_polyline_m']<5.8
    assert 0<row['polyline_approximation_error_m']<.001
    assert row['parent_mating_assessment_id'] and row['parent_route_intake_holds']
    assert row['parent_route_proposal']['physical_candidate_id']==route.PHYSICAL_CHILD
    assert definition['guide']['stock_cut_length_m']==2.9
    assert definition['belt']['stock_cut_length_m']==5.8
    assert definition['controlled_header_body_mount'] is None
    assert definition['controlled_pulley_shafts'] is None
    assert definition['controlled_belt_pitch_tension_and_tooth_count'] is None
    assert len(row['unresolved_inputs'])==5


def test_radius_outside_counted_pulley_envelope_preserves_failed_design():
    row=child.evaluate_radius(.05)
    assert row['disposition']=='infeasible-necessary-bound'
    assert any('envelope' in x for x in row['necessary_bound_failures'])
    assert row['physical_candidate_id']==identity(row['physical_definition'])
    assert row['sampled_belt_polyline_m'] is None
    assert row['parent_route_proposal'] is None
    assert row['parent_mating_assessment_id'] is None


@pytest.mark.parametrize('radius',[0.,-0.01,float('nan'),float('inf'),True])
def test_invalid_radius_refused(radius):
    with pytest.raises(ValueError,match='Finite positive'):
        child.evaluate_radius(radius)


def test_family_requires_small_distinct_sample_set():
    with pytest.raises(ValueError):child.evaluate_family([])
    with pytest.raises(ValueError):child.evaluate_family([.03,.03])
    with pytest.raises(ValueError):child.evaluate_family([.01]*13)
