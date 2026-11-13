"""Proposed door header geometry has distinct children and explicit holds."""
from copy import deepcopy
import json
from math import pi

import pytest

from engineering.station_rail.common import identity
from engineering.vehicle_parts import door_research_child as child
from tools.automation import v07_door_route as route


def test_parametric_children_have_ancestry_and_no_selection():
    request=json.loads(route.OUTPUT.read_bytes())
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
        assert 'parent_installed_evaluation_id' not in definition
        assert 'source_route_request_id' not in definition
        assert 'source' not in definition['proposed_car_local_header_frame']
        assert 'exact_ideal_pitch_length_hypothesis_m' not in definition['belt']
        assert 'supplier_limit_and_physical_test' not in definition
        assert row['parent_installed_evaluation_id']==request['installed_evaluation_id']
        assert row['source_route_request_id']==request['request_id']
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
    assert definition['belt']['proposed_centre_distance_m']==pytest.approx(b['ideal_centre_distance_m'])
    assert row['pitch_equals_cut_length_hypothesis'] is True
    assert len(row['unresolved_inputs'])==5


def test_evaluation_and_route_receipts_do_not_create_a_new_physical_child(monkeypatch):
    baseline=child.evaluate_radius(.03)
    handoff,request,handoff_raw,route_raw=child.door_mating._current_inputs(child.ROOT)
    changed=deepcopy(request)
    changed['installed_evaluation_id']='a'*64
    changed['request_id']='b'*64
    monkeypatch.setattr(child.door_mating,'_current_inputs',
        lambda root:(handoff,changed,handoff_raw,route_raw))
    monkeypatch.setattr(child.door_mating,'evaluate',
        lambda **kwargs:dict(assessment_id='e'*64,route_intake_holds=['synthetic held screen']))
    alternate=child.evaluate_radius(.03)
    assert alternate['physical_definition']==baseline['physical_definition']
    assert alternate['physical_candidate_id']==baseline['physical_candidate_id']
    assert alternate['evaluation_id']!=baseline['evaluation_id']


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
