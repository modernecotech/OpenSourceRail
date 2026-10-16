"""Independent static controls for staged return-rail demands and evidence scope."""

from copy import deepcopy
import json

import numpy as np
import pytest

from engineering.design_engine import factory_stages as s
from engineering.factory_examples import development


def rail(springs=(), elements=16):
    return s.Rail(8, 210e9, 1e-4, elements, list(springs))


def test_uniform_gravity_matches_independent_simply_supported_beam():
    r = rail()
    x = r.response(0, 0, distributed=-1200)
    a = r.actions(x, 1)
    assert a["pin_force_on_rail_n"] == pytest.approx([4800, 4800])
    assert a["maximum_additional_displacement_m"] == pytest.approx(
        5 * 1200 * 8**4 / (384 * 210e9 * 1e-4), rel=1e-9
    )
    assert abs(a["force_balance_n"]) < 1e-7
    assert abs(a["moment_balance_nm"]) < 1e-6


def test_equal_opposite_rotation_loads_match_constant_curvature():
    r = rail()
    x = r.response(0, 0, couple=15000)
    a = r.actions(x, 1)
    assert a["pin_force_on_rail_n"] == pytest.approx([0, 0], abs=1e-7)
    assert a["maximum_additional_displacement_m"] == pytest.approx(
        15000 * 8**2 / (8 * 210e9 * 1e-4)
    )
    assert x["displacements"][len(r.x) - 1, 0] < 0
    reverse = r.response(0, 0, couple=-15000)
    assert reverse["displacements"] == pytest.approx(-x["displacements"], abs=1e-10)


def test_staged_kernel_matches_existing_bow_and_rejects_instability():
    r = rail([(2, 1e6), (4, 1e6), (6, 1e6)])
    P = r.critical / 3
    actual = r.actions(r.response(P, 0.005), 1)
    control = development.imperfect_column(8, 210e9, 1e-4, 16, r.springs, P, 0.005)
    assert actual["brace_force_on_support_n"] == pytest.approx(
        [b["force_n"] for b in control["brace_reactions"]]
    )
    assert actual["maximum_additional_displacement_m"] == pytest.approx(
        control["additional_sway_m"]
    )
    assert r.response(r.critical, 0.005) is None


def test_combined_gravity_bow_and_couple_close_force_and_moment():
    r = rail([(2, 1e6), (4, 1e6), (6, 1e6)])
    for sign in (-1, 1):
        a = r.actions(
            r.response(r.critical / 2, 0.005, couple=20000, distributed=-1200), sign
        )
        assert abs(a["force_balance_n"]) < 1e-6
        assert abs(a["moment_balance_nm"]) < 1e-5
        assert a["free_force_residual_n"] < 1e-6
        assert a["free_moment_residual_nm"] < 1e-6


def sequence():
    rows = [
        dict(strand=str(i), strand_y_m=y, strand_z_m=z, force_per_strand_n=100)
        for i, (y, z) in enumerate([(-1, 0), (1, 0), (-1, 2), (1, 2)])
    ]
    return dict(
        sequences={
            "balanced_pairs": dict(stages=rows),
            "lower_first": dict(stages=rows),
        }
    )


def test_allocation_preserves_three_independent_resultants():
    forces = [(-1, 0, 100), (1, 2, 60), (-0.4, 1.2, 30)]
    a = s.allocate(forces, [-2, 2], 1)
    assert sum(a["axial_n"]) == pytest.approx(190)
    assert sum(y * P for y, P in zip([-2, 2], a["axial_n"])) == pytest.approx(-52)
    assert sum(a["end_couple_nm"]) == pytest.approx(-34)
    assert a["axial_n"][0] != a["axial_n"][1]
    with pytest.raises(ValueError):
        s.allocate([(3, 0, 100)], [-2, 2], 1)


def test_static_unloading_keeps_half_steps_and_finishes_at_zero():
    a = s.states(sequence(), "balanced_pairs", "reverse_stress", 2)
    b = s.states(sequence(), "balanced_pairs", "same_stress", 2)
    assert len(a) == 13
    assert a[5]["strand"] == "3" and b[5]["strand"] == "0"
    assert a[5]["remaining_fraction"] == 0.5
    assert sum(f for _, _, f in a[-1]["forces"]) == 0
    assert sum(f for _, _, f in a[4]["forces"]) == 400
    with pytest.raises(ValueError):
        s.states(sequence(), "balanced_pairs", "simultaneous", 2)


def test_historical_snapshot_integrity_does_not_require_current_sources(monkeypatch):
    from engineering.design_engine.factory_review import verify_snapshot
    from engineering.design_engine import registry

    folder = registry.ROOT / "docs/design-engine/factory-support"
    monkeypatch.setattr(registry, "dependencies", lambda _: {"changed": "source"})
    assert verify_snapshot(folder)["integrity_verified"]
    with pytest.raises(ValueError, match="earlier source revision"):
        verify_snapshot(folder, current=True)


def test_actual_common_stages_keep_pins_unknown_resistance_and_native_scope():
    from engineering.analysis.tests.test_design_factory import candidate

    c = candidate()
    a = c["definition"]["staged_loads"]
    assert a["stage_count"] == 145 and a["contact_cases_solved"] == 145 * 64
    assert a["stages"][0]["total_force_n"] == 0
    assert a["stages"][-1]["total_force_n"] == 0
    assert a["maximum_vertical_pin_force_n"] > 0
    assert a["rail_gravity_n_m"] < 0
    assert max(r["maximum_force_balance_residual_n"] for r in a["stages"]) < 1e-3
    assert max(r["maximum_moment_balance_residual_nm"] for r in a["stages"]) < 1e-2
    assert a["governing_cases"]["anchor"]["baseplate"]["resistance_qualified"] is False
    assert c["checks"]["staged_load_path"]["state"] == "unknown"
    assert c["installed_cost"] is None and c["physical_release"] is False
