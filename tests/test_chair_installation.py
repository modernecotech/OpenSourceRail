"""Pure small arithmetic/ownership controls; actual definition entrypoints forbidden.

These tests do not generate a chair coupon, a264-chair proposal, or any body,
CAD, FEM, city, cost campaign or business record. Local toy stock-cost arithmetic
tests verify missing/double-owned material cannot silently become zero.
"""
from copy import deepcopy
from math import pi

import pytest

from engineering import chair_installation as ci


@pytest.fixture(autouse=True)
def no_actual_definition_or_parent_read(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("source-only test attempted actual definition/receipt access")
    for name in ("chair_coupon", "bridge_definition", "read_parent", "source_layout",
                 "replacement_credits", "compile_proposal"):
        monkeypatch.setattr(ci, name, forbidden)


def test_frozen_fixed_interfaces_and_two_unevaluated_requests():
    recipe = ci.recipe_input()
    assert ci.validate_recipe(recipe)
    assert recipe["fixed"]["passenger_cg_z_m"] == 1.70
    assert recipe["fixed"]["extra_body_lift_m"] == 0
    requests = ci.trial_requests()
    assert len(requests) == 2
    assert sum(r["max_cpu_s"] for r in requests) == 120
    assert all(not r["automatic_admission"] and not r["physical_acceptance"] for r in requests)
    assert all(not r["native_CAD"] and not r["FEM"] and not r["body_producer"] for r in requests)


@pytest.mark.parametrize("key,value", [("chair_origin_m", 1.75), ("floor_top_m", 1.30),
    ("passenger_cg_z_m", 1.85), ("wheelchair_places", 0), ("chairs", 276)])
def test_second_lift_or_accessibility_change_is_rejected(key, value):
    r = ci.recipe_input(); r["fixed"][key] = value
    with pytest.raises(ValueError, match="fixed interface|lift"):
        ci.validate_recipe(r)


def test_gross_foam_stock_cannot_be_less_than_two_cut_pieces():
    r = ci.recipe_input(); r["geometry"]["foam_gross_cutset_m"][1] = .9
    with pytest.raises(ValueError, match="foam pieces"):
        ci.validate_recipe(r)


def test_shell_thickness_includes_actual_bondlines():
    r = ci.recipe_input(); r["geometry"]["skin_core_bondline_m"] = .0004
    with pytest.raises(ValueError, match="sandwich"):
        ci.validate_recipe(r)


def test_geometry_changes_need_a_new_explicit_recipe():
    r = ci.recipe_input(); r["geometry"]["backpost_u_m"] -= .01
    with pytest.raises(ValueError, match="frozen geometry"):
        ci.validate_recipe(r)


def test_no_inherited_acceptance_or_nonexistent_r1_bolt_credit():
    r = ci.recipe_input(); r["status"]["engineering_accepted"] = True
    with pytest.raises(ValueError, match="acceptance"):
        ci.validate_recipe(r)
    r = ci.recipe_input(); r["accounting"]["extra_r1_base_bolts_in_parent"] = True
    with pytest.raises(ValueError, match="nonexistent R1"):
        ci.validate_recipe(r)


def test_source_replacement_credit_ownership_is_exact_once():
    r = ci.recipe_input()
    r["accounting"]["source_parts_replaced_once"][-1] = r["accounting"]["source_parts_replaced_once"][0]
    with pytest.raises(ValueError, match="ownership"):
        ci.validate_recipe(r)


def test_rigid_handed_transform_does_not_add_body_lift():
    rz90 = [[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]]
    assert ci.transform([.2, .1, -.45], [2., -.94, 1.60], rz90) == pytest.approx([1.9, -.74, 1.15])
    with pytest.raises(ValueError, match="reflection"):
        ci.transform([0.,0.,0.], [0.,0.,0.], [[-1,0,0],[0,1,0],[0,0,1]])
    with pytest.raises(ValueError, match="orthonormal"):
        ci.transform([0.,0.,0.], [0.,0.,0.], [[2,0,0],[0,1,0],[0,0,1]])


def test_real_box_bore_removes_material_and_changes_centroid():
    e = ci.box("toy", [0.,0.,0.], [1.,1.,.1], "test", [ci.bore(2,[.2,0.,0.],.1)])
    v, c = ci.volume_centroid(e)
    removed = pi*.05**2*.1
    assert v == pytest.approx(.1-removed)
    assert c[0] == pytest.approx(-removed*.2/v)
    assert c[1:] == pytest.approx([0.,0.])


def test_blind_foam_relief_does_not_drill_through_front_surface():
    h = ci.bore(2,[0.,0.,0.],.1); h.update(depth_m=.02,entry_face=-1)
    e = ci.box("toy-foam", [0.,0.,0.], [.4,.4,.1], "test", [h])
    v,c = ci.volume_centroid(e)
    removed = pi*.05**2*.02
    assert v == pytest.approx(.016-removed)
    assert c[2] == pytest.approx(removed*.04/v)
    h["depth_m"] = .11
    with pytest.raises(ValueError, match="depth"):
        ci.box("bad", [0.,0.,0.],[.4,.4,.1],"test",[h])


def test_edge_breaking_bore_rejected_before_native_work():
    with pytest.raises(ValueError, match="blank edge"):
        ci.box("bad", [0.,0.,0.],[.1,.1,.01],"test",[ci.bore(2,[.049,0,0],.01)])


def test_rhs_is_four_nonoverlapping_walls_with_two_actual_bores():
    walls = ci.tube("toy",0,[0.,0.,0.],1.,[.1,.2],.01,"test",[ci.bore(2,[0,0,0],.02)])
    assert len(walls) == 4
    net = sum(ci.volume_centroid(e)[0] for e in walls)
    expected = (.1*.2-.08*.18) - 2*pi*.01**2*.01
    assert net == pytest.approx(expected)
    assert sum(len(e["bores"]) for e in walls) == 2
    with pytest.raises(ValueError, match="consumes void"):
        ci.tube("bad",0,[0,0,0],1.,[.1,.2],.05,"test")


@pytest.mark.parametrize("sign", [-1,1])
def test_signed_bolt_stack_contains_full_grip_washers_and_nut(sign):
    stack = ci.hardware_stack("toy",2,[0.,0.,0.],sign,
        [("plate-a",.006),("joint",.040),("plate-b",.006)], .070,.008,.0053,.0065)
    assert stack["nominal_thread_projection_m"] == pytest.approx(.0083)
    tip = ci.bounds(stack["entities"][1])[1 if sign > 0 else 0][2]
    assert tip == pytest.approx(sign*.070)
    assert stack["pieces"] == {"bolts":1,"nuts":1,"washers":2}
    assert not stack["tool_envelope"]["accepted"]
    with pytest.raises(ValueError, match="complete nut"):
        ci.hardware_stack("short",2,[0,0,0],sign,[("joint",.06)],.065,.008,.0053,.0065)


def test_counted_thicker_foot_keeps_floor_pan_and_lower_hardware_datums():
    r=ci.recipe_input(); g=r["geometry"]
    assert 1.60+g["leg_bottom_local_m"]-g["foot_size_m"][2] == pytest.approx(1.15)
    assert g["leg_bottom_local_m"]+g["leg_length_m"] == pytest.approx(-.0525)
    underhead=1.15+g["foot_size_m"][2]+.0005+.0016
    stack=ci.hardware_stack("fixture",2,[0.,0.,underhead],-1,
        [("head-isolation",.0005),("foot",g["foot_size_m"][2]),("strip",.003),
         ("structural-floor",.0375),("bridge",.060),("isolation",.001),("backing",.004)],
         g["floor_bolt_underhead_length_m"],.008,.0053,.0065)
    assert stack["nominal_thread_projection_m"] == pytest.approx(.0043)
    assert ci.bounds(stack["entities"][1])[0][2] == pytest.approx(1.0321)
    assert ci.bounds(stack["entities"][-1])[0][2] == pytest.approx(1.0364)


def test_shared_rest_has_one_owner_and_does_not_bridge_wc_gap():
    def seat(name,x):
        return dict(id=name,car=0,side=-1,origin_m=[x,-.94,1.6])
    rests = ci.owner_map([seat("a",0),seat("b",.48),seat("c",1.92),seat("d",2.4)])
    assert [(r["owner"],r["neighbour"]) for r in rests] == [("a","b"),("c","d")]
    assert all(r["local_v_sign"] == -1 for r in rests)
    with pytest.raises(ValueError, match="pitch"):
        ci.owner_map([seat("a",0),seat("b",.4)])


def test_actual_stub_width_not_old_reference_width_controls_anchor_choice():
    # Toy frame: local v is world X. A100mm stub excludes one row option;
    # choosing against an80mm stub would miss the required pad/margin.
    r = [[0.,1.,0.],[-1.,0.,0.],[0.,0.,1.]]
    rows = ci.choose_anchor_rows([.10,1.,1.6],r,[0.,.5])
    assert all(x["pad_stub_gap_m"] >= .005 for x in rows)
    for row in rows:
        for p in row["axes_world_m"]:
            assert min(abs(p[0]-x)-.05-.01 for x in [0.,.5]) >= .005
    with pytest.raises(ValueError, match="no floor-anchor"):
        ci.choose_anchor_rows([.10,1.,1.6],r,[-.09,.05,.15,.29])


def test_bridge_nodes_share_bolts_without_double_counting_adjacent_spans():
    anchors = [dict(id="a",at_m=[.25,1.,1.15]),dict(id="b",at_m=[.75,1.,1.15])]
    p = ci.bridge_plan(anchors,[0.,.5,1.],1.)
    assert len(p["spans"]) == 2
    assert len(p["nodes"]) == 3
    assert sum(n["through_bolt_sets"] for n in p["nodes"]) == 6
    assert sum(n["backing_plate_count"] for n in p["nodes"]) == 2
    assert p["nodes"][1]["connected_sides"] == ["left","right"]
    assert all(n["sleeve_length_m"] == .1 for n in p["nodes"])
    assert p["spans"][0]["rail_length_m"] == pytest.approx(.388)


@pytest.mark.parametrize("x", [-.2, .5, 1.2, .06])
def test_unsupported_or_overlapping_or_edge_anchor_never_becomes_bridge(x):
    with pytest.raises(ValueError):
        ci.bridge_plan([dict(id="bad",at_m=[x,1.,1.15])],[0.,.5,1.],1.)


def test_necessary_beam_bound_is_not_strength_qualification():
    a = ci.beam_bound(.9,[1000.,1000.],69e9,.04,.06,.003,60e6)
    b = ci.beam_bound(.45,[2000.],69e9,.04,.06,.003,60e6)
    assert a["deflection_bound_m"] == pytest.approx(8*b["deflection_bound_m"])
    assert a["stress_bound_Pa"] == pytest.approx(2*b["stress_bound_Pa"])
    assert not a["qualified"]
    with pytest.raises(ValueError, match="load domain"):
        ci.beam_bound(.9,[-1],69e9,.04,.06,.003,60e6)


def test_eccentric_foot_fixture_failure_cannot_hide_behind_column_capacity():
    # Tiny synthetic load fixture only; no actual chair definition is produced.
    loads=dict(occupant_kg=1.,provisional_chair_kg=1.,gravity_m_s2=10.,vertical_factor=1.,
               longitudinal_factor=1.,lateral_factor=1.,overturning_height_above_floor_m=.5)
    small=ci.chair_support_bounds(loads,[-.05,.05],allowable_stress=1e6)
    assert small["ideal_pin_column_euler_N"] > small["leg_compression_each_N"]
    assert small["foot_band_stress_residual_Pa"] < 0
    assert not small["fixture_band_screen_passed"] and not small["qualified"]
    loads["overturning_height_above_floor_m"] *= 2
    large=ci.chair_support_bounds(loads,[-.05,.05],allowable_stress=1e6)
    assert large["foot_band_stress_Pa"] == pytest.approx(2*small["foot_band_stress_Pa"])
    thicker=ci.chair_support_bounds(loads,[-.05,.05],allowable_stress=1e6,
                                    foot_thickness=.020,leg_length=.3775)
    assert thicker["foot_band_stress_Pa"] == pytest.approx(large["foot_band_stress_Pa"]*.04)
    # Even thicker stock need not pass an arbitrarily strict toy1MPa limit.
    assert not thicker["qualified"]
    assert thicker["fixture_band_screen_passed"] == (thicker["foot_band_stress_Pa"] <= 1e6)


def test_stock_mass_moment_and_cost_preserve_material_and_missing_scope():
    e = ci.box("toy",[.2,0.,0.],[.1,.2,.03],"toy")
    s = ci.stock_row("stock",[e],.001,.2,.1,"toy allowance")
    result = ci.stock_accounting([e],[s],dict(toy=dict(density_kg_m3=1000.,rate_usd_kg=[1,2,3])),[10.,0.,0.])
    assert result["net_nominal_material_mass_kg"] == pytest.approx(.6)
    assert result["gross_procurement_mass_kg"] == pytest.approx(1.)
    assert result["nominal_material_moment_kg_m"][0] == pytest.approx(.6*10.2)
    assert result["direct_material_process_QA_usd"]["base"] == pytest.approx(5.)
    assert not result["complete_installed"]
    assert s["tooling_allocation_usd"] is None
    with pytest.raises(ValueError,match="negative scrap"):
        ci.stock_row("bad",[e],.0001,.2,.1,"bad")
    with pytest.raises(ValueError,match="exactly once"):
        ci.stock_accounting([e],[s,deepcopy(s)],dict(toy=dict(density_kg_m3=1000.,rate_usd_kg=[1,2,3])))
    with pytest.raises(ValueError,match="exactly once"):
        ci.stock_accounting([e],[],dict(toy=dict(density_kg_m3=1000.,rate_usd_kg=[1,2,3])))


def test_density_bounds_are_not_silently_lost_from_mass_and_moments():
    e = ci.box("toy",[0.,0.,1.],[.1,.1,.1],"toy")
    s = ci.stock_row("stock",[e],.001,0.,0.,"pure stock fixture")
    result = ci.stock_accounting([e],[s],dict(toy=dict(density_kg_m3=1000.,density_bounds_kg_m3=[800.,1200.],rate_usd_kg=[1.,2.,3.])))
    assert result["net_material_mass_kg"] == pytest.approx(dict(low=.8,base=1.,high=1.2))
    assert result["net_material_moment_kg_m"]["high"] == pytest.approx([0.,0.,1.2])


def test_positive_group_allowances_retain_mass_moment_and_partial_scope():
    con = dict(welds=[dict(fillet_m=.003,net_length_m=.1,centroid_m=[0.,0.,1.])],
        anchor_sealant=dict(net_mass_kg=[.01,.02,.03],gross_mass_kg=[.02,.03,.04],
            centroid_hypothesis_m=[0.,0.,0.],process_hours=.1,qa_hours=.02))
    result = ci.consumable_accounting(con,dict(al6005a=dict(rate_usd_kg=[2.,4.,6.])),[0.,0.,2.])
    weld_mass=.5*.003**2*.1*2710.
    assert result["bounded_nonprimitive_mass_kg"]["base"] == pytest.approx(.02+weld_mass)
    assert result["bounded_nonprimitive_moment_kg_m"]["base"][2] == pytest.approx(.02*2+weld_mass*3)
    assert not result["actual_bead_cover_trim_geometry_complete"]


def test_floor_rectangle_clip_keeps_real_centroid_and_does_not_credit_outside():
    clip=ci.rectangle_intersection([0.,0.,0.],[2.,2.,.003],[.9,0.,0.],[.4,1.,.003])
    assert clip["area_m2"] == pytest.approx(.3)
    assert clip["centroid_xy_m"] == pytest.approx([.85,0.])
    assert ci.rectangle_intersection([0.,0.,0.],[2.,2.,.003],[2.,0.,0.],[.4,1.,.003]) is None


def test_geometry_fingerprint_excludes_qa_prices_and_acceptance_metadata():
    group=dict(net_mass_kg=[.01,.02,.03],centroid_hypothesis_m=[0.,0.,0.],qa_hours=.1)
    coupon=dict(entities=[ci.box("toy",[0.,0.,0.],[.1,.1,.1],"toy")],
        consumables=dict(welds=[dict(fillet_m=.003,net_length_m=.1,centroid_m=[0.,0.,0.],qualification="pending")],
            powder_coating=deepcopy(group),cover_seams=deepcopy(group),anchor_sealant=deepcopy(group)),
        price=10.,status=dict(physical_accepted=False))
    before=ci.identity(ci.coupon_geometry_projection(coupon))
    coupon["price"]=100.; coupon["status"]["physical_accepted"]=True
    coupon["consumables"]["cover_seams"]["qa_hours"]=50.
    assert before == ci.identity(ci.coupon_geometry_projection(coupon))
    coupon["entities"][0]["size_m"][0] += .001
    assert before != ci.identity(ci.coupon_geometry_projection(coupon))
