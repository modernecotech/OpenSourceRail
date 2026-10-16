"""Controls for fit, staged equilibrium and native fabrication primitives."""

import json
import math
import csv
import io
from copy import deepcopy

import pytest

from engineering.factory_examples import build, models, development, connections as c


@pytest.fixture(scope="module")
def context():
    p = build.PACKAGE / "data"
    a = json.loads((p / "basis.json").read_text())["assumptions"]
    i = json.loads((p / "development.json").read_text())
    cfg = json.loads((p / "connections.json").read_text())
    e = {
        v["id"]: v for v in json.loads((p / "equipment.json").read_text())["equipment"]
    }
    r = development.build(a, i, models.fixture(a), models.civil(a), e)
    candidate = next(
        v
        for v in r["prestress"]["alternatives"]
        if v["id"] == r["prestress"]["candidate_id"]
    )
    suppliers = json.loads((p / "fabrication-suppliers.json").read_text())
    return a, cfg, candidate, r, e, suppliers


@pytest.fixture(scope="module")
def result(context):
    return c.build(*context)


def test_grip_clash_and_revision_retained(result):
    s = result["strongback"]
    assert s["baseline_grip_fit"]["minimum_surface_gap_m"] == pytest.approx(-0.005)
    assert not s["baseline_grip_fit"]["geometric_clearance_screen"]
    assert s["revised_grip_fit"]["minimum_surface_gap_m"] == pytest.approx(0.01)
    assert s["revised_grip_fit"]["geometric_clearance_screen"]
    assert s["revised_grip_fit"]["exact_strand_grip_compatibility"] is None
    assert s["nominal_stem_side_cover_m"] == pytest.approx(0.0524)
    assert s["baseline_plate_grip_edge_clearance_m"] == pytest.approx(-0.0083333333333)
    assert s["revised_plate_grip_edge_clearance_m"] == pytest.approx(0.0416666666667)


def test_every_individual_stressing_step_satisfies_equilibrium(result):
    s = result["strongback"]
    assert s["axis_z_m"] == pytest.approx(1.2666666666667)
    for sequence in s["sequences"].values():
        assert len(sequence["stages"]) == 48
        torque = 0
        moment_y = 0
        for stage in sequence["stages"]:
            f = stage["force_per_strand_n"]
            torque += f * (stage["strand_z_m"] - s["axis_z_m"])
            moment_y += f * stage["strand_y_m"]
            left, right = stage["return_reactions_n"]
            assert left + right == pytest.approx(stage["total_stressing_force_n"])
            assert 1.85 * (right - left) == pytest.approx(moment_y, abs=1e-7)
            assert stage["end_vertical_couple_nm"] == pytest.approx(torque, abs=1e-7)
        assert sequence["final_end_couple_nm"] == pytest.approx(0, abs=1e-7)
        assert sequence["simultaneous_pair_stressing_assumed"] is False
    assert (
        s["sequences"]["balanced_pairs"]["maximum_abs_end_couple_nm"]
        < s["sequences"]["lower_first"]["maximum_abs_end_couple_nm"] / 5
    )
    assert s["physical_release"] is False


def test_unperforated_box_section_matches_independent_plate_properties(context, result):
    a, cfg, *_ = context
    s = result["strongback"]
    p = cfg["strongback"]
    d, h, t = p["box_depth_x_m"], p["box_height_z_m"], p["wall_m"]
    # Two x-face plates plus inner-width top and bottom plates; moment axis z.
    I = (
        2 * (h * t**3 / 12 + h * t * (d / 2 - t / 2) ** 2)
        + 2 * t * (d - 2 * t) ** 3 / 12
    )
    A = 2 * h * t + 2 * t * (d - 2 * t)
    assert s["box_area_m2"] == pytest.approx(A)
    assert s["box_in_plane_inertia_m4"] == pytest.approx(I)
    assert s["steel_resistance_pa"] is None


def test_ground_compliances_are_not_inferred_from_steel_post(context, result):
    s = result["strongback"]
    assert s["post_cantilever_stiffness_n_m"] > 1e6
    assert s["combined_effective_ground_restraint_n_m"] is None
    a, cfg, candidate, _, e, _ = context
    soft = deepcopy(cfg["strongback"])
    soft.update(
        ground_translation_n_m=1e6,
        base_rotation_nm_rad=1e6,
        connection_translation_n_m=1e6,
    )
    r = c.strongback(a, soft, candidate, e["ccl-sla15"])
    assert r["combined_effective_ground_restraint_n_m"] < 1e6
    assert not r["physical_release"]


def test_native_front_and_back_holes_match_all_48_grip_axes(context, result):
    parts = c.strongback_parts(context[1]["strongback"], result["strongback"])
    plates = [p for p in parts if p["id"] in ("strongback-inner", "strongback-outer")]
    grips = [p for p in parts if p["role"] == "grip-envelope"]
    assert len(grips) == 48
    changed = deepcopy(result["strongback"])
    changed.update(grip_outer_diameter_m=0.052, grip_body_length_m=0.110)
    changed_grips = [
        p
        for p in c.strongback_parts(context[1]["strongback"], changed)
        if p["role"] == "grip-envelope"
    ]
    assert all(
        g["size_m"] == pytest.approx([0.052, 0.052, 0.110]) for g in changed_grips
    )
    assert all(
        g["size_m"]
        == pytest.approx(
            [result["strongback"]["grip_outer_diameter_m"]] * 2
            + [result["strongback"]["grip_body_length_m"]]
        )
        for g in grips
    )
    assert len(plates) == 2
    for p in plates:
        assert len(p["holes"]) == 48
        centres = {
            (round(p["at_m"][1] + v["y_m"], 9), round(p["at_m"][2] + v["z_m"], 9))
            for v in p["holes"]
        }
        assert centres == {
            (round(g["at_m"][1] + 0.025, 9), round(g["at_m"][2] + 0.025, 9))
            for g in grips
        }
        gross = math.prod(p["size_m"])
        removed = 48 * math.pi * 0.022**2 / 4 * 0.04
        assert models.volume(p) == pytest.approx(gross - removed)


def test_retained_button_fit_contact_height_and_thread_unknowns(result):
    r = result["locator"]
    assert r["worst_case_diametral_clearance_m"] == pytest.approx([6e-6, 14e-6])
    assert r["contact_plane_z_m"] == pytest.approx(0.84)
    assert r["screw_nominal_engagement_m"] == pytest.approx(0.013)
    assert r["thread_resistance_n"] is None
    assert r["screw_preload_n"] is None


def test_blind_bore_and_two_wall_access_holes_remove_only_defined_material(context):
    parts = c.locator_parts(context[1]["locator"])
    rail = next(p for p in parts if p["id"] == "crossrail-coupon")
    gross = 0.3 * (0.05 * 0.1 - 0.04 * 0.09)
    removed = math.pi / 4 * (0.009**2 + 0.022**2) * 0.005
    assert models.volume(rail) == pytest.approx(gross - removed)
    pin = next(p for p in parts if p["id"] == "headed-locator-button")
    expected = math.pi / 4 * (0.01999**2 * 0.02 + 0.032**2 * 0.02 - 0.0068**2 * 0.016)
    assert models.volume(pin) == pytest.approx(expected)


def test_subcontract_range_screens_preserve_failed_girder_fit(result):
    cases = result["manufacturing"]["cases"]
    starcut = next(
        r
        for r in cases
        if r["part"] == "runway-girder" and r["supplier_case"] == "promil-starcut260"
    )
    responsive = next(
        r
        for r in cases
        if r["part"] == "runway-girder"
        and r["supplier_case"] == "responsive-horizontal"
    )
    assert not starcut["geometric_range_screen"]
    assert responsive["geometric_range_screen"]
    end = [r for r in cases if r["part"] == "strongback-end-steel"]
    assert end[0]["part_envelope_m"] == pytest.approx([4.6, 4, 1.9166666666667])
    assert end[0]["geometric_range_screen"]
    assert not end[1]["geometric_range_screen"]
    assert all(
        not r["payload_and_tool_access_accepted"] and r["price"] is None for r in cases
    )
    assert not result["manufacturing"]["new_machine_purchase_approved"]


def test_invalid_bearing_and_locator_nesting_rejected(context):
    a, cfg, candidate, _, e, _ = context
    bad = deepcopy(cfg["strongback"])
    bad["front_hole_diameter_m"] = 0.06
    with pytest.raises(ValueError, match="grip body"):
        c.strongback(a, bad, candidate, e["ccl-sla15"])
    bad = deepcopy(cfg["locator"])
    bad["stem_diameter_m"] = 0.021
    with pytest.raises(ValueError, match="nested"):
        c.locator_parts(bad)
    with pytest.raises(ValueError, match="unsupported"):
        models.volume(dict(kind="unrecognised", size_m=[1, 1, 1]))


def test_exported_sequence_is_explicitly_unissued():
    outputs, _ = build.make_outputs()
    rows = list(csv.DictReader(io.StringIO(outputs["stressing-sequence.csv"])))
    assert len(rows) == 48
    assert all(
        r["issued"] == "False" and r["revision"] == "2026-10-16-iteration-3"
        for r in rows
    )
    assert all(r["sequence_id"] == "balanced_pairs" for r in rows)
