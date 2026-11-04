from copy import deepcopy

import pytest

from engineering.design_search import design_grammar as g, frame_analysis as a, frame_section_refinement as r
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def body():return g.build(g.parameters())


def test_same_physical_frame_uses_actual_wall_torsion_and_replays_cache(tmp_path,body,monkeypatch):
    before=deepcopy(body)
    result=r.assess(body,tmp_path,maximum_new_jobs=1)
    assert result["execution"]=="completed"
    assert result["candidate_id"]==body["candidate_id"] and result["definition_id"]==body["definition_id"]
    assert body==before
    reference=r.frame_refinement.assess(body)["model"]
    restored=deepcopy(result["model"])
    restored["hypothesis_id"]=reference["hypothesis_id"]
    for member in restored["members"]:member["section"].pop("torsion_basis")
    assert restored==reference  # E/nu, loads, bending, roll, joints and supports stay identical.
    assert result["new_section_jobs"]==1 and result["reused_section_jobs"]==0
    assert result["section_studies"][0]["result"]["gate"]["state"]=="converged-under-declared-rule"
    assert all(p["torsion_model"]=="actual-wall-saint-venant-P1/1" for p in result["frame_result"]["member_properties"].values())
    assert result["native_admission"] is False and all(result[key] is False for key in r.frame_refinement.FLAGS)
    assert "shear-deformation-and-short-member-applicability-unresolved" in result["domain_holds"]
    def forbidden(*args,**kwargs):raise AssertionError("Cache replay launched a section solve")
    monkeypatch.setattr(r.section_torsion_job,"run",forbidden)
    monkeypatch.setattr(r.section_torsion,"spsolve",forbidden)
    cached=r.assess(body,tmp_path,maximum_new_jobs=0)
    assert cached["new_section_jobs"]==0 and cached["reused_section_jobs"]==1
    assert cached["model"]==result["model"] and cached["frame_result"]==result["frame_result"]


def test_zero_budget_and_unsupported_material_leave_torsion_unknown(tmp_path,body,monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError("Unrequested numerical section solve")
    monkeypatch.setattr(r.section_torsion_job,"run",forbidden)
    zero=r.assess(body,tmp_path,maximum_new_jobs=0)
    assert zero["model"] is None and zero["frame_result"] is None
    assert zero["domain_holds"]==["section-worker-budget-exhausted"]
    unknown=r.assess(g.build(g.parameters("gfrp_semimonocoque")),tmp_path,maximum_new_jobs=1)
    assert unknown["execution"]=="held" and unknown["new_section_jobs"]==0
    assert unknown["frame_result"] is None


@pytest.mark.parametrize("verified",[False,True])
def test_failed_or_unconverged_section_evidence_never_supplies_frame_stiffness(tmp_path,body,monkeypatch,verified):
    geometry={k:body["structure"]["members"][0]["section"][k] for k in ("width_m","height_m","wall_m")}
    request=r.section_torsion_job.request(geometry)
    (tmp_path/request["request_id"]).mkdir()
    monkeypatch.setattr(r.section_torsion_job,"verify",lambda *a,**k:dict(verified=verified,
        gate=dict(state="held",selected_J_m4=None,selected_evaluation_id=None)))
    def forbidden(*args,**kwargs):raise AssertionError("Unresolved section evidence reached frame assembly")
    monkeypatch.setattr(r,"_basis",forbidden)
    result=r.assess(body,tmp_path,maximum_new_jobs=0)
    assert result["model"] is None and result["frame_result"] is None
    assert result["execution"]=="held" and result["native_admission"] is False
    assert result["domain_holds"]==["section-torsion-numerical-evidence-unresolved"]


def test_supplied_torsion_changes_only_declared_torsional_stiffness():
    section=dict(width_m=.08,height_m=.16,wall_m=.004)
    properties=a.section_properties(section)
    basis=dict(schema="osr-section-torsion-basis/1",geometry=section,geometry_id=identity(dict(kind="rhs",**section)),
        J_m4=properties["J_thin_wall_m4"]*.5,method="actual-wall-saint-venant-P1/1",**{k:"0"*64 for k in
        ("request_id","selected_evaluation_id","source_epoch_id","runtime_id","convergence_rule_id")})
    basis["basis_id"]=identity(basis)
    refined=a.section_properties(dict(section,torsion_basis=basis))
    assert refined["J_used_m4"]==properties["J_thin_wall_m4"]*.5
    assert refined["area_m2"]==properties["area_m2"] and refined["I_y_m4"]==properties["I_y_m4"]
    assert refined["I_z_m4"]==properties["I_z_m4"]
    material=dict(E_Pa=70e9,G_Pa=70e9/(2*1.33))
    original=a._local_stiffness(3.,properties,material)
    updated=a._local_stiffness(3.,refined,material)
    assert updated[3,3]==original[3,3]*.5
    original[3,3]=updated[3,3];original[9,9]=updated[9,9];original[3,9]=updated[3,9];original[9,3]=updated[9,3]
    assert (original==updated).all()
    wrong=deepcopy(basis);wrong["geometry"]["width_m"]*=2;wrong["basis_id"]=identity({k:v for k,v in wrong.items() if k!="basis_id"})
    with pytest.raises(ValueError,match="same-geometry"):a.section_properties(dict(section,torsion_basis=wrong))
