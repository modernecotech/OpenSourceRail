import pytest

from engineering.powered_bogie.drive_geometry import compact_drive, axis_aligned_sweep
from engineering.powered_bogie.kinematic_tree import canonical_frames, compose, rigid
from engineering.powered_bogie.fit_closure import evaluate_all, evaluate_variant


def test_typed_transform_composition_maps_intended_frame():
    a = rigid("track/contact", "wheelset", (10, 0, 0))
    b = rigid("wheelset", "gear", (-1, 0, 0))
    assert compose(a, b).apply((0, 0, 0)) == (9, 0, 0)
    with pytest.raises(ValueError):
        compose(b, a)


def test_kinematic_tree_separates_primary_secondary_and_gear_motion():
    frames = canonical_frames(origin=(0, 0, .5), primary=.04, secondary=.04, gear_roll=.1)
    assert frames["track_to_wheelset"].child == "wheelset"
    assert frames["track_to_gear"].child == "gear"
    assert frames["track_to_body"].child == "body"
    assert frames["track_to_body"].apply((0, 0, 0))[2] == pytest.approx(.58)


def test_compact_drive_ratio_and_centres_close_arithmetically():
    d = compact_drive()
    assert d["calculated_ratio"] == pytest.approx(7.37)
    assert [s["centre_residual_m"] for s in d["stages"]] == pytest.approx([0, 0])
    assert d["counts_per_bogie"]["gear_bearings_positive_allowance"] == 6


def test_sweep_is_conservative_and_positive_box_required():
    swept = axis_aligned_sweep((0, 0, 0), (2, 2, 2), .1, .2)
    assert all(swept[i][0] < -1 and swept[i][1] > 1 for i in range(3))
    with pytest.raises(ValueError):
        axis_aligned_sweep((0, 0, 0), (0, 1, 1), .1, .2)


def test_exact_three_variants_are_held_and_identity_disciplined():
    results = evaluate_all()
    assert len(results) == 3
    assert all(r["poses_checked"] == 24 for r in results)
    assert all(r["engineering_screen"] == "HOLD" for r in results)
    assert results[0]["candidate_id"] == results[0]["parent_body_candidate_id"]
    assert results[1]["candidate_id"] != results[2]["candidate_id"]
    assert len(results[1]["bogie_coverage"]) == 12
    assert results[1]["relative_motion_sweeps"]["body_secondary_jounce_applied_to_running_gear"] is False
    assert results[1]["installation_bounds"]["floor_top_trial_bounds_after_rigid_body_lift_m"] == pytest.approx([1.2, 1.25])
    assert results[1]["installed_mass_cost_bounds"]["catalogue_mass_claim_subtotal_kg_per_bogie"] == pytest.approx(44.6)
    assert all(r["physical_accepted"] is False for r in results)
    with pytest.raises(ValueError):
        evaluate_variant("unlisted-variant")
