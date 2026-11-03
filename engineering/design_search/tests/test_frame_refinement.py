from copy import deepcopy

import pytest

from engineering.design_search import design_grammar as g, frame_refinement as f, native_refinement, topology_mutation
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def body():return g.build(g.parameters())


def reseal(candidate):
    candidate.pop("definition_id")
    candidate["definition_id"]=identity(candidate)
    return candidate


def test_frame_evaluation_preserves_physical_pin_graph_and_installed_unknowns(body):
    before=deepcopy(body)
    axial=native_refinement.assess(body)
    frame=f.assess(body)
    assert body==before
    assert axial["axial_diagnostic"]["mechanism_count"]>0
    assert frame["execution"]=="completed"
    assert frame["numerical_validity"]=="equilibrium-and-energy-confirmed-only"
    assert frame["native_admission"] is False
    assert "shear-deformation-and-short-member-applicability-unresolved" in frame["domain_holds"]
    assert frame["frame_result"]["domain"]["short_member_ids_advisory_lt_10"]
    assert frame["candidate_id"]==axial["candidate_id"]==body["candidate_id"]
    assert frame["definition_id"]==body["definition_id"]
    assert frame["complete_installed_mass_kg"] is None
    assert all(frame[k] is False for k in f.FLAGS)
    assert frame["whole_body_rejected"] is False and frame["integrated_selection"] is None
    assert frame["assessment_id"]==identity({k:v for k,v in frame.items() if k!="assessment_id"})


def test_supports_forces_and_rolls_are_explicit_same_candidate_projections(body):
    frame=f.assess(body);model=frame["model"]
    assert model["supports"]==body["structure"]["supports"]
    assert all(d<=3 for support in model["supports"] for d in support["dofs"])
    assert [{k:row[k] for k in ("node_id","force_N")} for row in model["loads"]]==body["structure"]["loads"]
    assert all(row["moment_Nm"]==[0.,0.,0.] for row in model["loads"])
    assert all(len(m["local_y"])==3 for m in model["members"])
    assert all(mat["nu"]==.33 and mat["law"]=="isotropic-linear-elastic-research" for mat in model["materials"].values())
    assert model["load_basis"]["missing_installed_mass_kg"] is None


@pytest.mark.parametrize("family",["gfrp_semimonocoque","pultruded_gfrp_frame"])
def test_axial_only_gfrp_law_remains_held(family):
    frame=f.assess(g.build(g.parameters(family)))
    assert frame["execution"]=="held" and frame["model"] is None
    assert "orthotropic law unavailable" in frame["reason"]
    assert frame["native_admission"] is False and frame["numerical_validity"]=="unknown"


@pytest.mark.parametrize("operator",topology_mutation.OPERATORS)
def test_branching_topologies_receive_separate_coarse_models(body,operator):
    candidate=topology_mutation.mutate(body,operator,requirement_revision=body["requirement_revision"])
    frame=f.assess(candidate)
    assert frame["model_id"]==identity(frame["model"])
    assert frame["frame_result"]["model_id"]==frame["model_id"]
    assert len(frame["model"]["members"])==len(candidate["physical"]["members"])
    assert frame["model"]["candidate_id"]==candidate["candidate_id"]!=body["candidate_id"]


def test_changed_elastic_hypothesis_is_an_evaluation_not_new_physical_candidate(body):
    first=f.assess(body);hyp=f.hypothesis();hyp["isotropic_aluminium_nu"]=.30
    second=f.assess(body,assumptions=hyp)
    assert first["candidate_id"]==second["candidate_id"]
    assert first["definition_id"]==second["definition_id"]
    assert first["hypothesis_id"]!=second["hypothesis_id"]
    assert first["model_id"]!=second["model_id"]
    assert first["comparison_context_id"]!=second["comparison_context_id"]


def test_missing_load_is_unknown_and_large_motion_holds_method(body):
    empty=deepcopy(body);empty["structure"]["loads"]=[]
    result=f.assess(reseal(empty))
    assert result["execution"]=="held" and "load case required" in result["reason"]
    adverse=deepcopy(body)
    for row in adverse["structure"]["loads"]:row["force_N"]=[v*100 for v in row["force_N"]]
    result=f.assess(reseal(adverse))
    assert "outside-small-displacement-frame-domain" in result["domain_holds"]
    assert result["native_admission"] is False and result["engineering_accepted"] is False


def test_singular_model_preserves_unsolved_execution(body):
    candidate=deepcopy(body);candidate["structure"]["supports"]=[]
    result=f.assess(reseal(candidate))
    assert result["execution"]=="held" and result["state"]=="held-unsolved-frame-model"
    assert result["frame_result"]["displacements_m"] is None
    assert result["native_admission"] is False


def test_identity_source_and_unsupported_hypothesis_fail_closed(body,monkeypatch):
    bad=deepcopy(body);bad["candidate_id"]="0"*64
    with pytest.raises(ValueError):f.assess(bad)
    hyp=f.hypothesis();hyp["joint_hypothesis"]="measured-rigid"
    with pytest.raises(ValueError,match="Unsupported frame hypothesis"):f.assess(body,assumptions=hyp)
    monkeypatch.setitem(f.LOADED,f.PRODUCER,"0"*64)
    with pytest.raises(ValueError,match="source changed"):f.assess(body)
