"""Independent support-contact equilibrium, tangents and adverse load paths."""

import json
import math

import pytest

from engineering.design_engine import factory_restraint as r
from engineering.design_engine.factory import ROOT
from engineering.analysis.tests.test_design_factory import candidate

ANCHORS = [[-0.16, -0.16], [-0.16, 0.16], [0.16, -0.16], [0.16, 0.16]]


def solve(N, M, strips=96):
    return r.contact(0.45, 0.45, ANCHORS, 1e12, 1e8, N, M, strips=strips)


def test_full_compression_matches_independent_uniform_bearing():
    a = solve(10000, 0)
    assert a["anchor_tensions_n"] == pytest.approx([0] * 4)
    assert a["contact_area_fraction"] == 1
    assert a["downward_translation_m"] == pytest.approx(10000 / (1e12 * 0.45**2))
    assert a["maximum_sampled_contact_pressure_pa"] == pytest.approx(10000 / 0.45**2)
    assert a["condensed_rotation_nm_rad"] == pytest.approx(
        1e12 * 0.45**4 / 12, rel=2e-4
    )


def test_full_uplift_uses_tension_only_anchors_and_no_grout_tension():
    a = solve(-10000, 0)
    assert a["anchor_tensions_n"] == pytest.approx([2500] * 4)
    assert a["contact_compression_n"] == 0
    assert a["downward_translation_m"] == pytest.approx(-10000 / (4e8))
    assert a["condensed_rotation_nm_rad"] == pytest.approx(
        1e8 * sum(y * y for _, y in ANCHORS)
    )


def test_partial_contact_satisfies_independent_continuous_force_and_moment():
    N, M = 5000, 5000
    a = solve(N, M, strips=192)
    u, theta = a["downward_translation_m"], a["rotation_rad"]
    lower, upper = max(-0.225, -u / theta), 0.225
    force = 1e12 * 0.45 * (u * (upper - lower) + theta * (upper**2 - lower**2) / 2)
    moment = (
        1e12
        * 0.45
        * (u * (upper**2 - lower**2) / 2 + theta * (upper**3 - lower**3) / 3)
    )
    assert force - sum(a["anchor_tensions_n"]) == pytest.approx(N, rel=0.003)
    assert moment - sum(
        T * y for T, (_, y) in zip(a["anchor_tensions_n"], ANCHORS)
    ) == pytest.approx(M, rel=0.003)
    assert abs(a["force_residual_n"]) < 1e-4
    assert abs(a["moment_residual_nm"]) < 1e-4
    assert 0 < a["contact_area_fraction"] < 1
    assert min(a["anchor_tensions_n"]) >= 0


def test_moment_reversal_and_condensed_tangent_match_independent_perturbation():
    a, reverse = solve(5000, 5000), solve(5000, -5000)
    assert reverse["rotation_rad"] == pytest.approx(-a["rotation_rad"])
    assert reverse["anchor_tensions_n"] == pytest.approx(
        list(reversed(a["anchor_tensions_n"]))
    )
    shifted = solve(5000, 5000.01)
    derivative = (shifted["rotation_rad"] - a["rotation_rad"]) / 0.01
    assert derivative == pytest.approx(1 / a["condensed_rotation_nm_rad"], rel=1e-5)
    fine = solve(5000, 5000, strips=192)
    assert max(fine["anchor_tensions_n"]) == pytest.approx(
        max(a["anchor_tensions_n"]), rel=0.01
    )


def test_pad_contact_transitions_preserve_force_and_moment():
    full = r.pad_pressure(2, 2, 100000, 10000)
    assert full["minimum_pressure_pa"] == pytest.approx(17500)
    assert full["maximum_pressure_pa"] == pytest.approx(32500)
    partial = r.pad_pressure(2, 2, 100000, 50000)
    c = partial["contact_length_m"]
    assert partial["maximum_pressure_pa"] * 2 * c / 2 == pytest.approx(100000)
    assert 1 - c / 3 == pytest.approx(50000 / 100000)
    assert r.pad_pressure(2, 2, 100000, 100001)["compression_equilibrium"] is False
    assert r.pad_pressure(2, 2, -100, 0)["compression_equilibrium"] is False


def test_series_compliance_does_not_invent_unknown_or_disconnected_interfaces():
    assert r.series(1e6, 1e6, 1e6, 1e6) == pytest.approx(250000)
    assert r.series(1e6, None) is None
    assert r.series(1e6, 0) == 0
    with pytest.raises(ValueError):
        r.series(1e6, -1)


def test_nominal_weld_line_demands_integrate_to_the_entered_actions():
    B, leg, N, M = 0.25, 0.006, 1000, 500
    row = r.weld_group(B, leg, N, M, 200)
    count = 10000
    ds = B / count
    y = (
        [(i + 0.5) * ds - B / 2 for i in range(count)] * 2
        + [-B / 2] * count
        + [B / 2] * count
    )
    sigma = [
        N / row["throat_area_m2"] + M * coordinate / row["line_inertia_m4"]
        for coordinate in y
    ]
    assert sum(sigma) * ds * row["throat_m"] == pytest.approx(N)
    assert sum(stress * coordinate for stress, coordinate in zip(sigma, y)) * ds * row[
        "throat_m"
    ] == pytest.approx(M, rel=1e-7)
    assert row["resistance_pa"] is None and row["wps_qualified"] is False


def test_common_export_packet_preserves_failed_cases_and_unknown_supplier_returns(
    tmp_path,
):
    from engineering.design_engine.factory_review import write_packet

    row = candidate()
    write_packet(row, tmp_path / "study")
    data = json.loads((tmp_path / "study/study.json").read_text())
    assert data["production_schedule"]["backlog_at_horizon"] > 0
    assert data["restraint"]["interface_cases"][0]["effective_lateral_n_m"] is None
    assert data["interface_supplier_enquiries"]["supplier_contacted"] is False
    assert all(
        case["offered_price_gbp"] is None
        for case in data["interface_supplier_enquiries"]["cases"]
    )
    assert (tmp_path / "study/review.svg").stat().st_size > 10000


def test_retained_native_snapshot_exact_bytes_reject_tampering(tmp_path):
    import shutil
    from engineering.design_engine.factory_review import verify_snapshot

    source = ROOT / "docs/design-engine/factory-support"
    assert verify_snapshot(source)["integrity_verified"]
    shutil.copytree(source, tmp_path / "snapshot")
    file = tmp_path / "snapshot/model.FCStd"
    file.write_bytes(file.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="integrity differs"):
        verify_snapshot(tmp_path / "snapshot")


def test_common_support_cases_keep_actual_unknown_and_soft_failure():
    row = candidate()
    study = row["definition"]["restraint"]
    assert len(study["cases"]) == 32
    assert (
        study["post_vertical_stiffness_n_m"] > 10 * study["post_lateral_stiffness_n_m"]
    )
    assert study["interface_cases"][0]["effective_lateral_n_m"] is None
    assert study["interface_cases"][1]["lateral_elastic_load_factor"] < 1
    assert study["interface_cases"][2]["lateral_requirement_met"] is False
    assert study["maximum_anchor_tension_n"] > 0
    assert row["checks"]["restraint_load_path"]["state"] == "unknown"
    failed = candidate(lateral_spring_n_m=0)["definition"]["restraint"]
    assert failed["cases"] == [] and failed["maximum_anchor_tension_n"] is None


def test_fixed_anchor_group_prevents_naive_baseplate_downsizing():
    row = candidate()
    cases = row["definition"]["restraint"]["baseplate_machining_cases"]
    assert cases[0]["pilot_cv5_diameter_screen"] is True
    assert cases[0]["geometric_edge_screen"] is False
    assert cases[1]["pilot_cv5_diameter_screen"] is False
    assert cases[1]["geometric_edge_screen"] is True
    cfg = json.loads(
        (ROOT / "engineering/design_engine/data/factory-restraint.json").read_text()
    )
    cfg["baseplate_m"][:2] = [0.35, 0.35]
    with pytest.raises(ValueError, match="breaks plate edge"):
        r.validate_basis(cfg)


def test_restraint_selection_is_not_the_legacy_one_meganewton_reference():
    row = candidate(lateral_spring_n_m=10000000)
    assert (
        row["definition"]["strongback"]["compliance_matches_selected_lateral_case"]
        is False
    )
    assert (
        row["definition"]["restraint"]["selected_lateral_requirement_n_m"] == 10000000
    )
