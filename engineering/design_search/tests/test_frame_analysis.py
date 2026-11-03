"""Independent closed-form checks of the bounded research frame model."""
from copy import deepcopy
from math import cos, sin

import numpy as np
import pytest

from engineering.design_search import frame_analysis as f
from engineering.station_rail.common import identity


def model(force=(0., 0., 0.), moment=(0., 0., 0.)):
    return dict(schema=f.SCHEMA, joint_hypothesis=f.JOINT,
        nodes=[dict(id="fixed", at_m=[0.,0.,0.]), dict(id="tip", at_m=[3.,0.,0.])],
        members=[dict(id="beam", start_node="fixed", end_node="tip", material_id="al",
            local_y=[0.,1.,0.], section=dict(width_m=.08, height_m=.16, wall_m=.004))],
        materials=dict(al=dict(law=f.LAW, E_Pa=70e9, nu=.33, density_kg_m3=2700., source_basis="Declared isotropic control")),
        supports=[dict(node_id="fixed", dofs=[1,2,3,4,5,6])],
        loads=[dict(node_id="tip", force_N=list(force), moment_Nm=list(moment))])


def properties(value):
    section=value["members"][0]["section"]
    b,h,t=section["width_m"],section["height_m"],section["wall_m"]
    return ((b*h-(b-2*t)*(h-2*t)), (b*h**3-(b-2*t)*(h-2*t)**3)/12,
            (h*b**3-(h-2*t)*(b-2*t)**3)/12,
            4*((b-t)*(h-t))**2/(2*(b+h-2*t)/t))


@pytest.mark.parametrize("kind", ["axial", "bend-y", "bend-z", "torsion", "moment-y", "moment-z"])
def test_independent_cantilever_closed_forms(kind):
    force, moment = [0.,0.,0.], [0.,0.,0.]
    if kind == "axial":force[0]=2000.
    elif kind == "bend-y":force[1]=1000.
    elif kind == "bend-z":force[2]=1000.
    elif kind == "torsion":moment[0]=100.
    elif kind == "moment-y":moment[1]=100.
    else:moment[2]=100.
    value=model(force,moment); a,iy,iz,j=properties(value); e=70e9; g=e/(2*1.33); l=3.
    result=f.evaluate(value); u=result["displacements_m"]["tip"]; r=result["rotations_rad"]["tip"]
    assert result["state"] == "completed-linear-frame-research-only"
    if kind == "axial":assert u[0] == pytest.approx(2000*l/(e*a),rel=1e-12)
    elif kind == "bend-y":
        assert u[1] == pytest.approx(1000*l**3/(3*e*iz),rel=1e-12)
        assert r[2] == pytest.approx(1000*l*l/(2*e*iz),rel=1e-12)
    elif kind == "bend-z":
        assert u[2] == pytest.approx(1000*l**3/(3*e*iy),rel=1e-12)
        assert r[1] == pytest.approx(-1000*l*l/(2*e*iy),rel=1e-12)
    elif kind == "torsion":assert r[0] == pytest.approx(100*l/(g*j),rel=1e-12)
    elif kind == "moment-y":
        assert r[1] == pytest.approx(100*l/(e*iy),rel=1e-12)
        assert u[2] == pytest.approx(-100*l*l/(2*e*iy),rel=1e-12)
    else:
        assert r[2] == pytest.approx(100*l/(e*iz),rel=1e-12)
        assert u[1] == pytest.approx(100*l*l/(2*e*iz),rel=1e-12)
    assert result["strain_energy_J"] == pytest.approx(result["external_work_J"],rel=1e-12)
    assert np.linalg.norm(result["force_equilibrium_residual_N"]) < 1e-8
    assert np.linalg.norm(result["moment_equilibrium_residual_Nm"]) < 1e-8
    assert all(result[k] is False for k in f.FLAGS)


def test_coordinate_and_explicit_roll_rotation_preserve_response_and_energy():
    value=model((100.,200.,300.),(10.,20.,30.)); original=deepcopy(value); result=f.evaluate(value)
    theta,phi=.43,.71
    rz=np.array([[cos(theta),-sin(theta),0.],[sin(theta),cos(theta),0.],[0.,0.,1.]])
    ry=np.array([[cos(phi),0.,sin(phi)],[0.,1.,0.],[-sin(phi),0.,cos(phi)]])
    q=rz@ry
    for node in value["nodes"]:node["at_m"]=(q@node["at_m"]).tolist()
    value["members"][0]["local_y"]=(q@value["members"][0]["local_y"]).tolist()
    for load in value["loads"]:
        load["force_N"]=(q@load["force_N"]).tolist();load["moment_Nm"]=(q@load["moment_Nm"]).tolist()
    rotated=f.evaluate(value)
    for field in ("displacements_m","rotations_rad","reactions_N","reaction_moments_Nm"):
        for node in ("fixed","tip"):
            assert rotated[field][node] == pytest.approx(q@result[field][node],rel=1e-10,abs=1e-10)
    assert rotated["strain_energy_J"] == pytest.approx(result["strain_energy_J"],rel=1e-11)
    assert rotated["member_end_forces_local"]["beam"] == pytest.approx(result["member_end_forces_local"]["beam"],rel=1e-10,abs=1e-9)
    assert original == model((100.,200.,300.),(10.,20.,30.))


def test_unrestrained_frame_is_held_without_zero_displacements_or_release():
    value=model((0.,0.,1000.));value["supports"]=[]
    result=f.evaluate(value)
    assert result["state"] == "held-singular-frame-model"
    assert result["displacements_m"] is result["strain_energy_J"] is None
    assert result["numerical"]["scaled_stiffness_rank"] < 12
    assert result["whole_body_rejected"] is False


def test_unknown_shear_or_anisotropic_material_and_missing_loads_are_not_zero():
    for change in ("nu","law","loads"):
        value=model((1000.,0.,0.))
        if change == "loads":value.pop("loads")
        else:value["materials"]["al"].pop(change)
        with pytest.raises(ValueError):f.evaluate(value)
    value=model();value["materials"]["al"]["G_Pa"]=1e9
    with pytest.raises(ValueError,match="Conflicting"):f.evaluate(value)


def test_explicit_shear_law_matches_poisson_law_and_inputs_are_immutable():
    value=model((0.,200.,300.),(100.,0.,0.)); snapshot=deepcopy(value)
    result=f.evaluate(value)
    assert value == snapshot
    shear=deepcopy(value);material=shear["materials"]["al"];nu=material.pop("nu");material["G_Pa"]=material["E_Pa"]/(2*(1+nu))
    assert f.evaluate(shear)["displacements_m"] == result["displacements_m"]
    assert result["model_id"] == identity(value)
    assert result["evaluation_id"] == identity({k:v for k,v in result.items() if k != "evaluation_id"})
    result["material_laws"]["al"]["E_Pa"]=1.
    assert value == snapshot


@pytest.mark.parametrize("kind", ["roll", "wall", "node", "support", "coordinate"])
def test_invalid_geometry_orientation_or_boundary_conditions_are_rejected(kind):
    value=model((0.,0.,100.))
    if kind == "roll":value["members"][0]["local_y"]=[1.,0.,0.]
    elif kind == "wall":value["members"][0]["section"]["wall_m"]=.05
    elif kind == "node":value["members"][0]["end_node"]="missing"
    elif kind == "support":value["supports"][0]["dofs"]=[7]
    else:value["nodes"][0]["at_m"][0]=float("nan")
    with pytest.raises(ValueError):f.evaluate(value)


def test_short_member_and_large_motion_stay_visible_without_engineering_admission():
    value=model((0.,0.,1e8));value["nodes"][1]["at_m"]=[.2,0.,0.]
    result=f.evaluate(value)
    assert result["domain"]["short_member_ids_advisory_lt_10"] == ["beam"]
    assert "unverified" in result["domain"]["status"]
    assert result["maximum_nodal_rotation_rad"] > .01
    assert result["engineering_accepted"] is False
