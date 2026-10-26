from copy import deepcopy
import math

import pytest

from engineering.design_search import guideway_tradeoff as study


def parent():
    return dict(candidate_id='a'*64,body_candidate_id='b'*64,magnet_component_id='c'*64,
        baseline=dict(civil_interface_id='d'*64,complete_counted_steel_stock_kg_per_span=21627.329447103097,
          reference_prismatic_concrete_volume_m3=17.,reference_prismatic_concrete_mass_kg=42500.,anchors_per_span=408,
          stock=[dict(id='protection/capture-cap',quantity=2,volume_m3=.02475,density_kg_m3=7850.,counted_mass_kg=388.575)]))


def test_thin_facing_fails_load_and_flux_capacity_not_inherited_force():
    p=parent();physical=study.definition('concrete-ledges',.012,.5,.45,.15,p)
    r=study.evaluate_variant(physical,p,70000.)
    assert r['necessary_screens']['local_elastic_deflection']=='fail'
    assert r['necessary_screens']['conditional_single_return_flux_capacity']=='fail'
    assert r['field_map']['actual_changed_interface_force_N'] is None
    assert r['field_map']['retained35mm_coupon_force_transferred'] is False
    assert r['physical_accepted'] is False


def test_elastic_strip_matches_independent_hand_fixture_and_scaling():
    r=study.plate_fixture(40000.,.5,.02)
    assert r['deflection_m']==pytest.approx(.001953125)
    assert study.plate_fixture(70000.,.5,.02)['deflection_m']/r['deflection_m']==pytest.approx(1.75)
    assert study.plate_fixture(40000.,1.,.02)['deflection_m']/r['deflection_m']==pytest.approx(8.)


def test_maxwell_flux_bound_uses_inequality_not_uniform_lobe_flux_guess():
    r=study.maxwell_bounds(40000.,.35,1.,1.6)
    assert r['conditional_one_section_minimum_thickness_m']==pytest.approx(.019634954084936204)
    assert r['predicts_actual_force'] is False
    assert r['field_cap_is_a_qualified_material_limit'] is False
    assert study.maxwell_bounds(70000.,.35,1.,1.6)['conditional_one_section_minimum_thickness_m']>.034
    with pytest.raises(ValueError):study.maxwell_bounds(float('nan'),.35,1.)


def test_changed_stock_counts_concrete_rebar_protection_and_every_anchor():
    p=parent();r=study.evaluate_variant(study.definition('embedded-edge-stiffeners',.035,1.,.55,.15,p),p)
    assert r['facing_anchors_per25m']==104
    assert r['additional_protection_base_anchors_per25m']==204
    assert r['all_support_anchors_per25m']==308
    assert r['additional_concrete_m3_per25m']>20.
    assert all(s['quantity']>0 and s['counted_mass_kg']>0 for s in r['stock'])
    assert sum(s['counted_mass_kg'] for s in r['stock'] if s['material']=='steel')==pytest.approx(r['steel_kg_per25m'])
    assert any(s['id'].startswith('retained/protection') for s in r['stock'])
    assert r['cost_break_even']['installed_price_per_direction_km'] is None
    assert r['cost_break_even']['new_protection_base_anchors']==204


def test_physical_identity_and_parent_mixing_are_rejected():
    p=parent();d=study.definition('concrete-ledges',.035,.5,.55,.15,p)
    bad=deepcopy(d);bad['facing_thickness_m']=.012
    with pytest.raises(ValueError,match='physical identity'):study.evaluate_variant(bad,p)
    other=deepcopy(p);other['magnet_component_id']='e'*64
    with pytest.raises(ValueError,match='another train or magnet'):study.evaluate_variant(d,other)


def test_support_pitch_is_not_a_free_cost_or_stiffness_saving():
    p=parent();a=study.evaluate_variant(study.definition('concrete-ledges',.035,.5,.55,.15,p),p)
    b=study.evaluate_variant(study.definition('concrete-ledges',.035,1.,.55,.15,p),p)
    assert b['facing_anchors_per25m']<a['facing_anchors_per25m']
    assert b['local_fixture']['plate_elastic_deflection_m']>7*a['local_fixture']['plate_elastic_deflection_m']
    assert b['necessary_screens']['local_elastic_deflection']=='fail'


def test_integral_ribs_reduce_concrete_but_keep_cages_feet_and_unknowns():
    p=parent();continuous=study.evaluate_variant(study.definition('dual-use-steel-box',.035,1.5,.55,.3,p),p,70000.)
    discrete=study.evaluate_variant(study.definition('dual-use-steel-box',.035,1.5,.55,.3,p,rib_width_x_m=.20),p,70000.)
    assert discrete['additional_concrete_m3_per25m']<continuous['additional_concrete_m3_per25m']/4
    assert discrete['all_support_anchors_per25m']==continuous['all_support_anchors_per25m']
    assert discrete['local_fixture']['RC_effective_longitudinal_width_m']==.20
    assert discrete['local_fixture']['RC_tie_yield_bound_N']>70000.
    assert discrete['local_fixture']['actual_shear_cracking_anchorage_and_fatigue_qualified'] is False
    assert any(s['id']=='protection-nib/U16-rebar' for s in discrete['stock'])
    assert any(s['id']=='head/rib-closed10-yield-truss-ties' for s in discrete['stock'])
    assert all(s['quantity']>0 and s['counted_mass_kg']>0 for s in discrete['stock'])
    assert discrete['physical_definition']['guideway_candidate_id']!=continuous['physical_definition']['guideway_candidate_id']


def test_narrow_rib_cannot_hide_insufficient_cage_space_or_stiffness():
    p=parent();d=study.definition('concrete-ledges',.035,.5,.55,.3,p,rib_width_x_m=.10)
    r=study.evaluate_variant(d,p,70000.)
    assert d['rib_transverse_bar_count']==0
    assert r['necessary_screens']['rib_cage_fit']=='fail'
    assert r['necessary_screens']['RC_fixture_flexure']=='fail'
    assert r['engineering_screen']=='failed-necessary-screen'
