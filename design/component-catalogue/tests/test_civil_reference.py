import pytest

from osr_mech.civil.foundation import foundation_candidates, foundation_concrete_m3, select_foundation, select_ground_improvement
from osr_mech.civil.reference import DETAIL_MASSES, RIGGING_MASSES, lifting_budget, compare_foundations


@pytest.mark.parametrize("count", [0,-1,1.5,True,float("nan"),float("inf")])
def test_explicit_invalid_count_never_uses_default(count):
    with pytest.raises(ValueError): foundation_concrete_m3("bored-shaft",actual_length_m=18,actual_element_count=count)


@pytest.mark.parametrize("length", [float("nan"),float("inf"),0,-1,True])
def test_nonfinite_or_invalid_deep_length(length):
    with pytest.raises(ValueError): foundation_concrete_m3("bored-shaft",actual_length_m=length)


def test_ground_category_returns_candidates_without_site_selection():
    r=foundation_candidates("urban-alluvium",vibration_restricted=True)
    assert len(r["candidate_ids"]) > 1 and r["selected_id"] is None
    legacy=select_foundation("urban-alluvium")
    assert legacy.selected_id is None and legacy.selection_state == "planning-preference-only"
    with pytest.raises(ValueError,match="chemistry"): select_ground_improvement("weak-formation")


def test_pi25_requires_complete_mass_and_actual_lift_chart():
    incomplete=lifting_budget(25,{}, {})
    assert incomplete["bare_mass_kg"] == pytest.approx(74937.5)
    assert incomplete["bare_margin_kg"] == pytest.approx(62.5)
    assert not incomplete["lifting_check_passed"]
    masses={k:0. for k in (*DETAIL_MASSES,*RIGGING_MASSES)}
    masses.update(net_diaphragms=1000,spreader=2000)
    lift=dict(equipment_id="TEST",chart_reference="TEST",configuration="TEST",radius_m=12,capacity_at_radius_kg=75000,dynamic_factor=1.1,permitted_utilisation=.9,review_reference="TEST",support_check_reference="TEST",stability_check_reference="TEST",mass_basis_reference="TEST")
    r=lifting_budget(25,masses,lift)
    assert r["complete_member_mass_kg"] == pytest.approx(75937.5)
    assert not r["member_target_met"] and not r["lifting_check_passed"]
    lift["capacity_at_radius_kg"]=100000
    heavy=lifting_budget(25,masses,lift)
    assert heavy["equipment_capacity_met"] and not heavy["overall_accepted"]
    assert not heavy["lifting_check_passed"] and heavy["status"] == "member-target-exceeded"
    deviation=dict(decision="accepted",engineer="designer",checker="independent checker",signed_at="2026-10-02",controlled_reference="TEST",rationale="Test heavier product",mass_budget_sha256=heavy["mass_budget_sha256"])
    approved=lifting_budget(25,masses,lift,product_deviation=deviation)
    assert approved["overall_accepted"] and approved["controlled_deviation_accepted"]
    masses["net_diaphragms"]+=1
    assert not lifting_budget(25,masses,lift,product_deviation=deviation)["overall_accepted"]
    assert lifting_budget(20,masses,lift)["overall_accepted"]
    lift["capacity_at_radius_kg"]=1
    assert not lifting_budget(20,masses,lift)["overall_accepted"]


def test_site_comparison_requires_capacity_settlement_and_review():
    site=dict(groundwater="TEST",chemistry="TEST",liquefaction="TEST",scour="TEST",utilities="TEST",construction_access="TEST",axial_demand_kN=1000,lateral_demand_kN=100,settlement_limit_mm=10,differential_settlement_limit_mm=5)
    row=dict(id="bored-shaft",axial_capacity_kN=1500,lateral_capacity_kN=150,settlement_mm=12,differential_settlement_mm=2,constructable=True,chemistry_compatible=True,liquefaction_checked=True,scour_checked=True,calculation_reference="TEST")
    assert compare_foundations([row["id"]],[row],site)["feasible_candidates"] == []
    row["settlement_mm"]=8
    assert compare_foundations([row["id"]],[row],site)["selected_id"] is None
    site["selection_review"]=dict(selected_id=row["id"],decision="accepted",engineer="TEST designer",checker="TEST checker",signed_at="2026-10-02",controlled_reference="TEST",comparison_rationale="TEST comparison")
    assert compare_foundations([row["id"]],[row],site)["selected_id"] == row["id"]
