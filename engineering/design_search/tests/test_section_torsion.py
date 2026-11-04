"""Independent geometry/series/variational controls for actual-wall torsion."""
from math import pi, tanh
from copy import deepcopy

import numpy as np
import pytest

from engineering.design_search import section_torsion as s
from engineering.station_rail.common import identity


def section(t=.004):
    return dict(width_m=.08,height_m=.16,wall_m=t)


def rectangle_series(width,height):
    # Independent Saint-Venant rectangle Fourier series, no fitting to FEM.
    b,h=max(width,height),min(width,height)
    odd=range(1,1002,2)
    return b*h**3/3*(1-192*h/(pi**5*b)*sum(tanh(n*pi*b/(2*h))/n**5 for n in odd))


@pytest.mark.parametrize("width,height", [(1.,1.),(2.,1.),(.5,1.)])
def test_solid_rectangle_independent_series_and_nested_upper_energy(width,height):
    exact=rectangle_series(width,height)
    results=[s.rectangle(width,height,divisions=n) for n in (16,32,64)]
    values=[v["J_energy_m4"] for v in results]
    assert all(a>=b for a,b in zip(values,values[1:]))
    assert values[-1]>=exact*(1-1e-11)
    assert values[-1] == pytest.approx(exact,rel=7e-4)
    if width==height==1.:
        assert exact == pytest.approx(.140577014955,rel=1e-10)


def test_actual_rhs_keeps_void_and_exact_four_wall_area_inertias():
    geometry=section()
    result=s.evaluate(geometry,through_wall=4)
    b,h,t=geometry.values()
    assert result["quantities"]["area_m2"] == pytest.approx(b*h-(b-2*t)*(h-2*t),rel=1e-12)
    assert result["quantities"]["area_m2"] < b*h
    assert max(result["quantity_relative_errors"].values()) < 1e-12
    assert "hole" in result["mesh"]["material_domain"]
    assert 0<result["J_energy_m4"]<result["quantities"]["polar_inertia_m4"]
    assert all(result[k] is False for k in s.FLAGS)
    assert result["evaluation_id"] == identity({k:v for k,v in result.items() if k != "evaluation_id"})


def test_nested_wall_refinement_and_independent_energy_torque_checks():
    results=[s.evaluate(section(),through_wall=n) for n in (1,2,4,8)]
    assert all(a["J_energy_m4"]>=b["J_energy_m4"] for a,b in zip(results,results[1:]))
    assert all(a["mesh"]["node_count"]<b["mesh"]["node_count"] for a,b in zip(results,results[1:]))
    for value in results:
        assert value["numerical"]["weak_residual_relative"] < 1e-10
        assert value["J_energy_m4"] == pytest.approx(value["J_torque_m4"],rel=1e-10)
        assert value["J_energy_m4"] == pytest.approx(value["J_stationary_m4"],rel=1e-10)


def test_gauge_and_width_height_symmetry_do_not_change_torsion():
    first=s.evaluate(section(),through_wall=2)
    other=s.evaluate(section(),through_wall=2,gauge_node=first["mesh"]["node_count"]-1)
    swapped=s.evaluate(dict(width_m=.16,height_m=.08,wall_m=.004),through_wall=2)
    assert first["J_energy_m4"] == pytest.approx(other["J_energy_m4"],rel=1e-11)
    assert first["J_energy_m4"] == pytest.approx(swapped["J_energy_m4"],rel=1e-11)
    assert first["model_id"] != other["model_id"]
    assert first["geometry_id"] == other["geometry_id"]


def test_geometric_scaling_has_fourth_power_J_and_no_material_modulus():
    original=s.evaluate(section(),through_wall=2)
    scaled=s.evaluate({key:3*v for key,v in section().items()},through_wall=2)
    assert scaled["J_energy_m4"] == pytest.approx(81*original["J_energy_m4"],rel=1e-11)
    assert "G_Pa" not in scaled and "E_Pa" not in scaled


def test_thin_wall_limit_approaches_bredt_without_fitting_or_enforcement():
    relative=[]
    for wall in (.004,.002,.001):
        b,h=.08,.16
        result=s.evaluate(section(wall),through_wall=2)
        bredt=4*((b-wall)*(h-wall))**2/(2*(b+h-2*wall)/wall)
        relative.append(abs(result["J_energy_m4"]-bredt)/bredt)
    assert relative[2]<relative[1]<relative[0]
    assert relative[-1]<.01


@pytest.mark.parametrize("bad", [None,0,-1,True,float("nan"),float("inf")])
def test_unknown_or_invalid_geometry_cannot_become_zero(bad):
    value=section();value["wall_m"]=bad
    with pytest.raises(ValueError):s.evaluate(value)


def test_solid_shortcut_unsupported_resolution_and_bad_gauge_are_rejected():
    with pytest.raises(ValueError,match="positive hole"):s.evaluate(dict(width_m=1.,height_m=1.,wall_m=.5))
    with pytest.raises(ValueError,match="geometry only"):s.evaluate(dict(section(),G_Pa=1.))
    with pytest.raises(ValueError,match="resolution"):s.evaluate(section(),through_wall=3)
    with pytest.raises(ValueError,match="gauge"):s.evaluate(section(),gauge_node=True)


def test_oversize_is_rejected_before_any_mesh_array_allocation(monkeypatch):
    monkeypatch.setattr(s,"_mesh",lambda *args,**kwargs:pytest.fail("oversize geometry allocated a mesh"))
    with pytest.raises(ValueError,match="before allocation"):
        s.evaluate(dict(width_m=1.,height_m=2.,wall_m=1e-7),through_wall=8)


def test_saved_nodal_field_replays_exactly_without_invoking_a_solver(monkeypatch):
    rhs=s.evaluate(section(),through_wall=2)
    solid=s.rectangle(1.,1.,divisions=16)
    monkeypatch.setattr(s,"spsolve",lambda *a,**k:pytest.fail("verification invoked a sparse solver"))
    assert s.verify(section(),rhs)["verified"]
    assert s.verify_result(solid)["verified"]
    assert len(rhs["warping_m2"])==rhs["mesh"]["node_count"]
    assert rhs["mesh_id"]==rhs["mesh"]["mesh_id"]
    rhs.pop("warping_m2")
    rhs["evaluation_id"]=identity({k:v for k,v in rhs.items() if k!="evaluation_id"})
    with pytest.raises(ValueError,match="required for solve-free"):
        s.verify_result(rhs)


@pytest.mark.parametrize("kind", ["warping","scalar-J","geometry","source","mesh"])
def test_consistently_resealed_changed_warping_scalar_or_binding_is_rejected(kind):
    value=deepcopy(s.evaluate(section(),through_wall=1))
    if kind=="warping":value["warping_m2"][1]+=.0001
    elif kind=="scalar-J":value["J_energy_m4"]*=1.01
    elif kind=="geometry":value["geometry"]["wall_m"]*=1.1
    elif kind=="source":value["source_sha256"][s.PRODUCER]="0"*64
    else:value["mesh_id"]="0"*64
    value["evaluation_id"]=identity({k:v for k,v in value.items() if k!="evaluation_id"})
    with pytest.raises(ValueError):s.verify_result(value)


def test_explicit_expected_worker_runtime_changes_only_declared_thread_metadata(monkeypatch):
    value=s.evaluate(section())
    child=deepcopy(value["runtime"])
    child["numerical_thread_environment"]={name:"1" for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS")}
    value["runtime"]=child
    value["evaluation_id"]=identity({k:v for k,v in value.items() if k!="evaluation_id"})
    for name in child["numerical_thread_environment"]:monkeypatch.delenv(name,raising=False)
    assert s.verify_result(value,expected_runtime=child)["verified"]
    forged=deepcopy(child);forged["scipy"]="other-library"
    with pytest.raises(ValueError,match="worker runtime"):
        s.verify_result(value,expected_runtime=forged)
