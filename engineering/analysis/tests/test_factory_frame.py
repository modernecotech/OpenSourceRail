"""Independent spatial stiffness, load/geometry and finite-base controls."""

import json
import math
from pathlib import Path
import numpy as np
import pytest
from scipy.linalg import solve

from engineering.design_engine import factory_frame as f
from osr_mech.section_contract import rhs


def cantilever():
    section = rhs(0.2, 0.3, 0.01, density_kg_m3=7850)
    return dict(
        nodes_m=[[0, 0, 0], [2, 0, 0]],
        members=[
            dict(
                id="control",
                i=0,
                j=1,
                offset_i_m=[0, 0, 0],
                offset_j_m=[0, 0, 0],
                section=section,
            )
        ],
        springs=[dict(node=0, k=[1e18] * 6)],
        young_pa=210e9,
        poisson=0.3,
        gravity_load=[0] * 12,
    )


def test_three_dimensional_axial_bending_and_torsion_match_closed_forms():
    model = cantilever()
    section = model["members"][0]["section"]
    K = f.system(model)
    for dof, load, expected in [
        (0, 1000, 1000 * 2 / (210e9 * section["area_m2"])),
        (1, 1000, 1000 * 2**3 / (3 * 210e9 * section["iz_m4"])),
        (2, 1000, 1000 * 2**3 / (3 * 210e9 * section["iy_m4"])),
        (3, 1000, 1000 * 2 / (210e9 / 2.6 * section["j_torsion_m4"])),
    ]:
        F = np.zeros(12)
        F[6 + dof] = load
        u = solve(K, F, assume_a="pos")
        assert u[6 + dof] == pytest.approx(expected, rel=1e-7)
        eq = f.balance(model, F, u)
        assert max(map(abs, eq["force_residual_n"])) < 1e-7
        assert max(map(abs, eq["moment_residual_nm"])) < 1e-7


def test_rigid_arm_preserves_virtual_work_and_force_moment():
    r = np.array([0.45, 0, -0.25])
    H = f.arm(r)
    wrench = np.array([1000, 2000, 3000, 5, 6, 7])
    u = np.array([1, 2, 3, 0.01, 0.02, 0.03])
    assert wrench @ (H @ u) == pytest.approx((H.T @ wrench) @ u)
    assert (H.T @ wrench)[3:] == pytest.approx(wrench[3:] + np.cross(r, wrench[:3]))


def test_no_ground_springs_leaves_a_mechanism():
    model = cantilever()
    model["springs"][0]["k"] = [0] * 6
    eigen = np.linalg.eigvalsh(f.system(model))
    assert sum(abs(eigen) < 1e-4) >= 6


@pytest.fixture(scope="module")
def candidate():
    from engineering.analysis.tests.test_design_factory import candidate

    return candidate()


def test_whole_bed_has_two_heads_full_rails_and_sixteen_supports(candidate):
    native = candidate["definition"]["native_model"]
    study = candidate["definition"]["spatial_frame"]
    assert len(native["parts"]) == 376
    rails = [p for p in native["parts"] if p["role"] == "return-rail-steel"]
    assert len(rails) == 2 and all(p["size_m"][0] == 26 for p in rails)
    assert sum(p["role"] == "post-steel" for p in native["parts"]) == 16
    assert sum(p["role"] == "foundation-reservation" for p in native["parts"]) == 16
    assert len(study["model"]["springs"]) == 16
    assert all(
        study["model"]["nodes_m"][s["node"]][0] in [3, 6, 9, 12, 15, 18, 21, 24]
        for s in study["model"]["springs"]
    )
    assert len({p["id"] for p in native["parts"]}) == 376


def test_native_steel_gravity_and_six_axis_global_balance_reconcile(candidate):
    study = candidate["definition"]["spatial_frame"]
    model = study["model"]
    assert -sum(model["gravity_load"][2::6]) / 9.80665 == pytest.approx(
        model["represented_steel_mass_kg"]
    )
    assert study["equilibrium_verified"]
    assert all(
        max(map(abs, r["force_residual_n"])) < r["force_tolerance_n"]
        for r in study["stages"]
    )
    assert all(
        max(map(abs, r["moment_residual_nm"])) < r["moment_tolerance_nm"]
        for r in study["stages"]
    )
    assert len(study["native_cases"]) == 2
    assert model["actual_ground"] is None
    assert candidate["checks"]["spatial_frame"]["state"] == "unknown"
    assert candidate["checks"]["spatial_native"]["state"] == "unknown"
    assert candidate["physical_release"] is False


def test_handover_cannot_promote_development_to_physical_design_acceptance(tmp_path):
    import importlib.util
    import shutil

    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "factory_handover", root / "tools/automation/factory-buildout.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    folder = root / "docs/design-engine/factory-buildout"
    assert module.verify(folder, current=True)["engineering_design_complete"] is False
    shutil.copytree(folder, tmp_path / "handover")
    record = json.loads((tmp_path / "handover/handover.json").read_text())
    record["engineering_design_complete"] = True
    (tmp_path / "handover/handover.json").write_text(json.dumps(record))
    with pytest.raises(ValueError, match="cannot grant"):
        module.verify(tmp_path / "handover")


def test_handover_detects_extra_or_tampered_review_artifacts(tmp_path):
    import importlib.util
    import shutil

    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "factory_handover_integrity", root / "tools/automation/factory-buildout.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    shutil.copytree(root / "docs/design-engine/factory-buildout", tmp_path / "handover")
    (tmp_path / "handover/unreviewed.txt").write_text("extra")
    with pytest.raises(ValueError, match="membership"):
        module.verify(tmp_path / "handover")
    (tmp_path / "handover/unreviewed.txt").unlink()
    (tmp_path / "handover/index.html").write_text("changed")
    with pytest.raises(ValueError, match="index integrity"):
        module.verify(tmp_path / "handover")
