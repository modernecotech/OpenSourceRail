import json
from math import cos, sin

import pytest

from engineering.design_search import solid_torsion_native as s
from engineering.station_rail.common import digest, encoded, identity


def test_actual_hole_volume_shared_quadratic_nodes_and_positive_cells():
    value=s.model();mesh=s.mesh(value);coords={n["id"]:n["at_m"] for n in mesh["nodes"]}
    assert len(mesh["elements"]) == 128
    assert len(mesh["nodes"]) == 976
    assert len({tuple(p) for p in coords.values()}) == len(coords)
    assert mesh["stock_volume_m3"] == pytest.approx((.08*.16-.072*.152)*1.5,rel=1e-12)
    assert all(len(set(row))==20 for row in mesh["elements"])
    for element in mesh["elements"]:
        a,b,c,d=[coords[element[i]] for i in (0,1,3,4)]
        assert b[0]>a[0] and c[1]>a[1] and d[2]>a[2]
        centre_y=(a[1]+c[1])/2;centre_z=(a[2]+d[2])/2
        assert not (abs(centre_y)<.036 and abs(centre_z)<.076)
        assert coords[element[8]] == pytest.approx([(x+y)/2 for x,y in zip(a,b)])
    text=s.deck(value,mesh)
    assert "TYPE=C3D20R" in text and "*SOLID SECTION" in text
    assert "SECTION=BOX" not in text and "TYPE=B32R" not in text
    assert "BASE,1,3" in text


@pytest.mark.parametrize("torque",[1.,-2.])
def test_declared_end_force_couple_has_zero_force_and_exact_torque(torque):
    value=s.model(torque_Nm=torque);mesh=s.mesh(value)
    assert mesh["applied_force_N"] == pytest.approx([0.,0.,0.],abs=1e-12)
    assert mesh["applied_torque_Nm"] == pytest.approx(torque,rel=1e-12)
    assert all(p["weight_m2"]>0 for p in mesh["section_points"])


def test_full_and_reduced_integration_have_separate_mesh_identity_and_deck():
    value=s.model();a=s.mesh(value,element_kind="C3D20R");b=s.mesh(value,element_kind="C3D20")
    assert a["nodes"] == b["nodes"] and a["elements"] == b["elements"]
    assert a["model_id"] == b["model_id"] and a["mesh_id"] != b["mesh_id"]
    assert "TYPE=C3D20,ELSET" in s.deck(value,b)
    assert "TYPE=C3D20R,ELSET" in s.deck(value,a)
    with pytest.raises(ValueError,match="integration"):s.mesh(value,element_kind="B32R")


def test_closed_wall_flow_changes_load_hypothesis_without_changing_geometry():
    polar=s.model();flow=s.model(loading_hypothesis="geometry-normalised-closed-wall-shear-flow")
    a=s.mesh(polar);b=s.mesh(flow)
    assert a["nodes"]==b["nodes"] and a["elements"]==b["elements"]
    assert a["model_id"]!=b["model_id"] and a["loads"]!=b["loads"]
    assert b["applied_force_N"]==pytest.approx([0.,0.,0.],abs=1e-12)
    assert b["applied_torque_Nm"]==pytest.approx(1.,rel=1e-12)
    assert set(b["wall_face_owner_counts"])=={"top","bottom","left","right"}
    assert b["wall_face_owner_counts"]["top"]==b["wall_face_owner_counts"]["bottom"]


def test_direct_central_gradient_and_work_recovery_from_synthetic_motion_fixture(tmp_path):
    value=s.model();mesh=s.mesh(value);rate=1e-4;length=value["length_m"]
    displacements={}
    for n in mesh["nodes"]:
        x,y,z=n["at_m"];angle=rate*x
        displacements[n["id"]]=[.01*y*z,(cos(angle)-1)*y-sin(angle)*z,sin(angle)*y+(cos(angle)-1)*z]
    keys={tuple(n["grid_key"]):n["id"] for n in mesh["nodes"]};reactions={n:[0.,0.,0.] for n in mesh["base_node_ids"]}
    for section,load in zip(mesh["section_points"],mesh["loads"]):
        reactions[keys[0,*section["grid_key"]]]=[-v for v in load["force_N"]]
    work=.5*sum(sum(a*b for a,b in zip(load["force_N"],displacements[load["node_id"]])) for load in mesh["loads"])
    path=tmp_path/"synthetic.dat"
    path.write_text("displacements\n"+"\n".join(str(n)+" "+" ".join(f"{v:.16g}" for v in u) for n,u in displacements.items())+
        "\nforces\n"+"\n".join(str(n)+" "+" ".join(f"{v:.16g}" for v in r) for n,r in reactions.items())+
        f"\ntotal internal energy\n{work:.16g}\n")
    result=s.analyse(value,mesh,path)
    expected=value["torque_Nm"]/(value["E_Pa"]/(2*(1+value["nu"]))*rate)
    assert result["J_interior_gradient_m4"] == pytest.approx(expected,rel=1e-10)
    assert result["central_gradient_relative_spread"]<1e-10
    assert result["J_vertex_corner_gradient_m4"] == pytest.approx(expected,rel=1e-10)
    assert result["J_midplane_corner_gradient_m4"] == pytest.approx(expected,rel=1e-10)
    assert not result["calibration_admission"]
    assert result["torque_relative_residual"]<1e-12
    assert result["energy_work_relative_residual"]<1e-12
    assert result["global_energy_is_end_effect_diagnostic_only"]


def test_no_solver_preparation_and_immutable_verification(tmp_path,monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError("No native solver allowed")
    monkeypatch.setattr(s.subprocess,"run",forbidden)
    path=tmp_path/"prepared";result=s.run(s.model(),path)
    assert result["execution"]=="not-run" and result["native_jobs_used"]==0
    before={p.name:digest(p) for p in path.iterdir()}
    assert s.verify(path)["evaluation_id"]==result["evaluation_id"]
    assert before=={p.name:digest(p) for p in path.iterdir()}
    with pytest.raises(FileExistsError):s.run(s.model(),path)


def test_missing_tool_remains_held(tmp_path,monkeypatch):
    monkeypatch.setattr(s.frame_native,"_tool",lambda:None)
    result=s.run(s.model(),tmp_path/"missing",execute=True)
    assert result["execution"]=="held" and result["native_jobs_used"]==0


def test_invalid_hole_mesh_and_discrete_limits_rejected():
    with pytest.raises(ValueError,match="hole"):s.mesh(s.model(wall_m=.04))
    with pytest.raises(ValueError,match="eight"):s.mesh(s.model(),axial_elements=4)
    with pytest.raises(ValueError,match="budget"):s.mesh(s.model(),axial_elements=64,width_divisions=16,height_divisions=32,through_wall=4)
    with pytest.raises(ValueError,match="counts"):s.mesh(s.model(),through_wall=True)


def test_payload_and_resealed_completion_tamper_is_rejected(tmp_path):
    path=tmp_path/"prepared";s.run(s.model(),path)
    result=json.loads((path/"result.json").read_bytes());result.update(execution="completed",native_jobs_used=1)
    result.pop("evaluation_id");result["evaluation_id"]=identity(result);(path/"result.json").write_bytes(encoded(result))
    manifest=json.loads((path/"manifest.json").read_bytes());manifest["evaluation_id"]=result["evaluation_id"]
    manifest["files_sha256"]["result.json"]=digest(path/"result.json");manifest.pop("manifest_id");manifest["manifest_id"]=identity(manifest)
    (path/"manifest.json").write_bytes(encoded(manifest))
    with pytest.raises(ValueError,match="job count"):s.verify(path)
