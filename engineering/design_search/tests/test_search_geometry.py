"""Exact hollow stock and immutable candidate-bound handoffs, without CAD jobs."""
from copy import deepcopy
import json

import numpy as np
import pytest

from engineering.design_search import design_grammar as g, railway_bundle
from engineering.design_search import search_geometry as geometry
from engineering.station_rail.common import digest, encoded, identity


@pytest.fixture(scope="module")
def pair():
    body=g.build(dict(g.parameters(),braced=True))
    return body,railway_bundle.materialize(body)


def box():
    return dict(id="box/control",kind="box",at_m=[1.,2.,3.],size_m=[.1,.2,2.],volume_m3=.04)


def tube():
    start=np.array([1.,2.,3.]);end=np.array([2.,4.,6.])
    return dict(id="tube/control",kind="oriented-RHS",start_m=start.tolist(),end_m=end.tolist(),
        width_m=.08,height_m=.16,wall_m=.006,
        volume_m3=(.08*.16-.068*.148)*float(np.linalg.norm(end-start)))


def reseal(folder):
    path=folder/"manifest.json";manifest=json.loads(path.read_bytes())
    manifest["files_sha256"]=geometry._inventory(folder)
    manifest["manifest_id"]=identity({k:v for k,v in manifest.items() if k!="manifest_id"})
    path.write_bytes(encoded(manifest))


def test_box_surface_is_exact_outward_and_closed():
    value=geometry.mesh(box())
    assert len(value["vertices_m"])==8 and len(value["triangles"])==12
    assert value["surface_euler_characteristic"]==2
    assert value["bore_count"]==0 and value["closed_surface"] is True
    assert value["mesh_volume_m3"]==pytest.approx(.04,rel=1e-12)


def test_oriented_rhs_preserves_hole_four_walls_and_volume():
    part=tube();value=geometry.mesh(part)
    assert len(value["vertices_m"])==16 and len(value["triangles"])==32
    assert value["surface_euler_characteristic"]==0 and value["bore_count"]==1
    assert value["mesh_volume_m3"]==pytest.approx(part["volume_m3"],rel=1e-11)
    assert value["native_volume_m3"]<.08*.16*np.linalg.norm(np.subtract(part["end_m"],part["start_m"]))
    vertices=np.asarray(value["vertices_m"])
    basis=geometry.grammar_geometry.basis(part)
    local=(vertices-np.asarray(part["start_m"]))@basis
    assert sorted(set(np.round(np.abs(local[:,:2]).ravel(),8)))==[.034,.04,.074,.08]


def test_rhs_axes_and_translation_do_not_change_actual_stock_volume():
    for end in ([3.,2.,3.],[1.,4.,3.],[1.,2.,5.],[-1.,2.,3.]):
        part=tube();part["end_m"]=end
        part["volume_m3"]=(.08*.16-.068*.148)*2
        assert geometry.mesh(part)["mesh_volume_m3"]==pytest.approx(part["volume_m3"],rel=1e-10)


@pytest.mark.parametrize("change",[
    {"wall_m":.04},{"wall_m":None},{"wall_m":float("nan")},
    {"end_m":[1.,2.,3.]},{"volume_m3":0.},{"volume_m3":float("nan")},
    {"kind":"fabricated-joint"},{"volume_m3":3.},
])
def test_invalid_stock_never_becomes_placeholder_solid(change):
    with pytest.raises((ValueError,TypeError)):
        geometry.mesh(dict(tube(),**change))


def test_plan_binds_whole_railway_and_body_stock_without_claiming_complete_geometry(pair):
    body,bundle=pair;plan=geometry.prepare(body,bundle)
    assert plan["candidate_id"]==bundle["candidate_id"]!=body["candidate_id"]
    assert plan["body_candidate_id"]==body["candidate_id"]
    assert plan["body_definition_id"]==body["definition_id"]
    assert plan["occurrence_count"]==len(body["parts"])
    assert plan["execution"]=="not-requested"
    assert plan["complete_installed_geometry"] is False
    assert all(plan[k] is False for k in geometry.FLAGS)
    assert plan["plan_id"]==identity({k:v for k,v in plan.items() if k!="plan_id"})


def test_unrequested_build_and_read_only_replay_never_call_native_tools(pair,tmp_path,monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError("Native generation was not requested")
    monkeypatch.setattr(geometry.grammar_geometry,"export",forbidden)
    monkeypatch.setattr(geometry.wheel_twin,"_ifc",forbidden)
    monkeypatch.setattr(geometry,"_tool",forbidden)
    folder=tmp_path/"handoff";result=geometry.build(*pair,folder)
    assert result["verified"] is True and result["native_CAD_jobs"]==0
    assert result["native_CAD"] is None and result["IFC"] is None
    assert geometry.verify(*pair,folder)==result
    assert set(geometry._inventory(folder))=={"result.json","mesh.json"}
    with pytest.raises(ValueError,match="Fresh"):
        geometry.build(*pair,folder)


@pytest.mark.parametrize("key,value",[
    ("physical_accepted",True),("complete_installed_geometry",True),
    ("scope","Complete installed train"),("schema","unknown/1"),
    ("candidate_id","0"*64),("native_CAD_jobs",True),
    ("execution","completed-known-stock"),("surprise",0),
])
def test_resealed_false_result_claims_are_rejected(pair,tmp_path,key,value):
    folder=tmp_path/"handoff";geometry.build(*pair,folder)
    result=json.loads((folder/"result.json").read_bytes());result[key]=value
    (folder/"result.json").write_bytes(encoded(result));reseal(folder)
    with pytest.raises(ValueError):geometry.verify(*pair,folder)


def test_resealed_mesh_hole_and_source_tampering_are_rejected(pair,tmp_path):
    folder=tmp_path/"handoff";geometry.build(*pair,folder)
    record=json.loads((folder/"mesh.json").read_bytes())
    record["rows"][0]["bore_count"]=20
    (folder/"mesh.json").write_bytes(encoded(record));reseal(folder)
    with pytest.raises(ValueError,match="exact current body stock"):
        geometry.verify(*pair,folder)


def test_extra_payload_symlink_duplicate_keys_and_hash_changes_are_rejected(pair,tmp_path):
    folder=tmp_path/"handoff";geometry.build(*pair,folder)
    (folder/"extra.log").write_text("unrequested")
    reseal(folder)
    with pytest.raises(ValueError,match="extra native payload"):
        geometry.verify(*pair,folder)
    (folder/"extra.log").unlink()
    (folder/"extra.log").symlink_to(folder/"result.json")
    with pytest.raises(ValueError,match="paths"):
        geometry.verify(*pair,folder)
    duplicate=tmp_path/"duplicate.json";duplicate.write_text('{"a":1,"a":2}')
    with pytest.raises(ValueError,match="Duplicate"):
        geometry._read(duplicate)


def test_mixed_body_and_resealed_bundle_definition_fail_closed(pair):
    body,bundle=pair
    other=g.build(dict(g.parameters(),braced=True,chord_wall_m=.008))
    with pytest.raises(ValueError):geometry.prepare(other,bundle)
    changed=deepcopy(bundle);changed["body_definition_id"]="0"*64
    changed["definition_id"]=identity({k:v for k,v in changed.items() if k!="definition_id"})
    with pytest.raises(ValueError,match="different body"):
        geometry.prepare(body,changed)


def test_current_loaded_source_guard_and_job_budget_are_enforced(pair,tmp_path,monkeypatch):
    key=geometry.PRODUCER
    monkeypatch.setitem(geometry.LOADED,key,"0"*64)
    with pytest.raises(ValueError,match="source changed"):
        geometry.prepare(*pair)
    monkeypatch.setitem(geometry.LOADED,key,digest(geometry.__file__))
    for invalid in (True,-1,2,None):
        with pytest.raises(ValueError,match="zero-or-one"):
            geometry.build(*pair,tmp_path/str(invalid),native_cad_jobs=invalid)


def test_exact_native_input_adds_rhs_basis_without_mutating_candidate(pair):
    body,_=pair;before=deepcopy(body)
    value=geometry._native_input(body)
    assert value["candidate_id"]==body["candidate_id"]
    assert all("basis" in p and "length_m" in p for p in value["parts"] if p["kind"]=="oriented-RHS")
    assert body==before
