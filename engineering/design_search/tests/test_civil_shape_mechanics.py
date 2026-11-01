"""Independent arithmetic, identity and evidence controls for civil mechanics."""
from copy import deepcopy
import gzip
import json
import pytest

from engineering.design_search import civil_shape_mechanics as m
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def inputs():
    spec=m.specification(); context=m.load_context()
    result,compressed=m.parent._calculate()
    candidates=json.loads(gzip.decompress(compressed))
    rows={r["candidate_id"]:r for r in result["evaluations"]}
    return spec,context,candidates,rows


def case(inputs,family="reference_box",profile="reference",model_name=None,load_name="normal",mass_name="base"):
    spec,context,candidates,rows=inputs
    c=next(c for c in candidates if c["family"]==family and c["profile"]==profile)
    row=rows[c["candidate_id"]]
    models=m.sections.models(c,spec["elastic_moduli_Pa"])
    model=models[0] if model_name is None else next(x for x in models if x["name"]==model_name)
    load=next(x for x in context["cases"] if x["name"]==load_name)
    mass=next(x for x in row["cost_estimate"]["cases"] if x["case"]==mass_name)
    return c,row,model,load,mass,spec,context


def test_complete_train_axle_count_and_single_dynamic_factor(inputs):
    spec,context,*_=inputs
    assert context["cars"]==6
    for load in context["cases"]:
        assert len(load["offsets_m"])==24 and load["maximum_simultaneous_axles"]==6
        expected=load["accounted_mass_kg_per_car"]*m.civil.G/4*1.3
        assert load["force_N_per_full_axle"]==expected
        assert load["equivalent_live_moment_upper_udl_N_m"]==6*expected/10
    assert m.maximum_axles_inside([0,2,7,9],2)==2
    for offsets,span in (([],20),([float("nan")],20),([0],0)):
        with pytest.raises(ValueError):m.maximum_axles_inside(offsets,span)


def test_reference_box_upper_bound_matches_closed_form_not_a_sampled_maximum(inputs):
    args=case(inputs);result=m.evaluate_case(*args)
    q=result["accounted_span_mass_kg"]*m.civil.G/20+args[3]["equivalent_live_moment_upper_udl_N_m"]
    ei=35e9*.30360192
    expected=q*20**4/(60*ei)
    assert result["all_pose_all_observation_model_deflection_upper_m"]==pytest.approx(expected,rel=1e-12)
    expected_stress=(q*20**2/8)*.7/.30360192
    assert result["stress_upper"]["material_demands"]["research_concrete"]["tension_Pa"]==pytest.approx(expected_stress)
    assert result["representative_sampled_deflection_m"]<expected
    assert result["representative_response"]["deflection_at_observation_m"][0]==0
    assert abs(result["representative_response"]["deflection_at_observation_m"][-1])<1e-12
    assert result["installed_dead_load_complete"] is False
    assert result["physical_deflection_upper_bound_available"] is False
    assert result["physical_strength_or_deflection_acceptance_limit"] is None
    assert result["stress_upper"]["resistance_credited"] is False


def test_hybrid_keeps_concrete_gravity_without_granting_composite_action(inputs):
    steel=m.evaluate_case(*case(inputs,"hybrid_steel_concrete",model_name="steel-only-longitudinal"))
    bonded=m.evaluate_case(*case(inputs,"hybrid_steel_concrete",model_name="perfect-bond-uncracked"))
    assert steel["candidate_id"]==bonded["candidate_id"] and steel["section_model_id"]!=bonded["section_model_id"]
    assert steel["accounted_span_mass_kg"]==bonded["accounted_span_mass_kg"]
    assert steel["cells"][0]["distributed_load_N_m"]==bonded["cells"][0]["distributed_load_N_m"]
    assert steel["all_pose_all_observation_model_deflection_upper_m"]>bonded["all_pose_all_observation_model_deflection_upper_m"]
    assert steel["stress_upper"]["concrete_longitudinal_stress_calculated"] is False
    assert "research_concrete" not in steel["stress_upper"]["material_demands"]
    assert bonded["stress_upper"]["concrete_longitudinal_stress_calculated"] is True


def test_mass_reserves_change_gravity_not_physical_identity_or_stiffness(inputs):
    low=m.evaluate_case(*case(inputs,mass_name="low"));high=m.evaluate_case(*case(inputs,mass_name="high"))
    assert low["candidate_id"]==high["candidate_id"] and low["section_model_id"]==high["section_model_id"]
    assert low["cells"][0]["EI_Nm2"]==high["cells"][0]["EI_Nm2"]
    assert low["accounted_span_mass_kg"]<high["accounted_span_mass_kg"]
    assert low["all_pose_all_observation_model_deflection_upper_m"]<high["all_pose_all_observation_model_deflection_upper_m"]


def test_lifting_uses_piece_mass_and_adjusts_erection_cost_once(inputs):
    c,row,model,load,mass,spec,context=case(inputs)
    lift=m.lifting(c,row,spec);base=lift["cases"][1]
    expected=(row["quantities"]["total_nominal_stock_mass_kg"]+mass["preliminary_reinforcement_kg"]+mass["unsized_prestress_reserve_kg"])*1.25
    assert base["required_hook_kg_hypothesis"]==pytest.approx(expected)
    assert base["exceeds_nominal_capacity_hypothesis"] is True
    original=row["cost_estimate"]["line_items_iqd"]["erection"]["base"]
    assert base["adjusted_erection_iqd"]==pytest.approx(original*(expected/60000)**1.5,abs=.01)
    assert base["lift_adjusted_scoped_installed_iqd"]==pytest.approx(
        mass["scoped_installed_iqd"]+base["adjusted_erection_iqd"]-original,abs=.01)
    assert not lift["actual_crane_suitable"] and not lift["installed_lift_mass_complete"]


def test_mixed_or_resealed_wrong_geometry_loads_and_mass_are_rejected(inputs):
    args=list(case(inputs));wrong=case(inputs,"folded_plate")
    for index,match in ((1,"parent quantity"),(2,"section model"),(4,"mass case")):
        changed=deepcopy(args);changed[index]=deepcopy(wrong[index])
        with pytest.raises(ValueError,match=match):m.evaluate_case(*changed)
    changed=deepcopy(args);changed[2]["cells"][0]["EI_Nm2"]*=10
    changed[2]["evaluation_id"]=identity({k:v for k,v in changed[2].items() if k!="evaluation_id"})
    with pytest.raises(ValueError,match="section model"):m.evaluate_case(*changed)
    changed=deepcopy(args);changed[3]["force_N_per_full_axle"]*=.1
    with pytest.raises(ValueError,match="sealed comparison context"):m.evaluate_case(*changed)
    changed=deepcopy(args);changed[6]["context_id"]="0"*64
    with pytest.raises(ValueError,match="sealed comparison context"):m.evaluate_case(*changed)
    changed=deepcopy(args)
    load=changed[6]["cases"][1]
    load["accounted_mass_kg_per_car"]*=.5
    load["force_N_per_full_axle"]*=.5
    load["maximum_simultaneous_axle_force_N"]*=.5
    load["equivalent_live_moment_upper_udl_N_m"]*=.5
    changed[3]=load
    changed[6]["context_id"]=identity({k:v for k,v in changed[6].items() if k!="context_id"})
    with pytest.raises(ValueError,match="selected physical vehicle"):m.evaluate_case(*changed)


def test_publication_covers_all_hypotheses_preserves_diversity_and_rejects_tampering(tmp_path):
    out=tmp_path/"mechanics";result=m.build(output=out)
    assert result["verified"] and result["candidate_count"]==18 and result["calculated_case_count"]==189
    assert result["retained_candidates"]==18
    value=json.loads(gzip.decompress((out/"result.json.gz").read_bytes()))
    assert len(value["section_models"])==21
    assert len({c["load_context_id"] for c in value["cases"]})==1
    assert max(c["force_equilibrium_residual_N"] for c in value["cases"])<1e-6
    assert all(row["stage_1_complete"] is False and row["stage_2_admission"] is False for row in value["evaluations"])
    assert all(value[key] is False for key in m.FLAGS)
    assert m.verify(output=out)==result
    (out/"result.json.gz").write_bytes(b"changed")
    with pytest.raises(ValueError,match="payload differs"):m.verify(output=out)
    with pytest.raises(ValueError,match="payload differs"):m.build(output=out)
