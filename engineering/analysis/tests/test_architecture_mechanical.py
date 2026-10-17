"""Independent LM3 axle identity, equilibrium and architecture feedback controls."""

import json

import pytest

from engineering.generative_design import architecture_mechanical as a


@pytest.fixture(scope="module")
def report():
    return a.run()


def test_exact_six_lm3_cases_and_unaccepted_loading_boundary(report):
    expected = {
        "lm3-source-reference",
        "lm3-gap-1p8",
        "lm3-gap-2p0",
        "lm3-gap-1p8-frame-750x25",
        "lm3-gap-2p0-frame-750x25",
        "lm3-gap-1p8-lighter-built-up-i",
    }
    assert {c["id"] for c in report["cases"]} == expected
    for case in report["cases"]:
        assert case["architecture_id"] == "LM3"
        assert (
            case["body_count"] == 3
            and case["bogie_count"] == 6
            and case["axle_count"] == 12
        )
        assert not case["accepted_loading"]
        assert not case["source_frozen_baseline"]
        assert not case["engineering_design_complete"]
        assert not case["physical_release"]
        assert case["existing_configuration_compatible"] == (
            case["id"] == "lm3-source-reference"
        )
    assert not report["input_trace_accepted"]
    assert not report["six_car_transfer"]["lm3_frame_delta_transferred"]
    assert report["six_car_transfer"]["accepted_axle_distribution"] is None
    assert all(not s["accepted"] for s in report["source_references"])


def test_retained_source_axle_ids_forces_and_actual_local_offsets(report):
    source = json.loads(a.TRACE.read_text())["reference"]
    pattern = {x["id"]: x for x in source["axle_pattern"]}
    for case in report["cases"]:
        assert len({x["id"] for x in case["axles"]}) == 12
        assert {x["id"] for x in case["axles"]} == set(pattern)
        for axle in case["axles"]:
            original = pattern[axle["id"]]
            car = axle["car_index"]
            assert axle["source_force_n"] == original["static_load_kn"] * 1000
            assert axle["x_m"] == pytest.approx(
                original["x_m"] + (car - 1) * case["inter_car_gap_m"]
            )
            assert axle["local_x_m"] == pytest.approx(
                original["x_m"] - (car - 1) * 16.5
            )
        for car in case["cars"]:
            assert car["source_axle_local_positions_m"] == pytest.approx(
                [1.05, 3.15, 13.35, 15.45]
            )


def test_gaps_change_complete_car_positions_and_length(report):
    for case in report["cases"]:
        gap = case["inter_car_gap_m"]
        assert case["train_length_m"] == pytest.approx(49.5 + 2 * gap)
        assert [c["centre_x_m"] for c in case["cars"]] == pytest.approx(
            [8.25, 24.75 + gap, 41.25 + 2 * gap]
        )
        assert case["horizontal_mass_cg_x_m"] == pytest.approx(
            case["train_length_m"] / 2
        )
        assert case["force_cg_x_m"] == pytest.approx(case["train_length_m"] / 2)


def test_mixed_gravity_preserves_source_and_adds_only_declared_delta(report):
    baseline = report["cases"][0]
    original_force = sum(x["force_n"] for x in baseline["axles"])
    assert original_force == pytest.approx(105750 * 9.81)
    assert original_force != pytest.approx(105750 * 9.80665, abs=1e-6)
    for case in report["cases"]:
        delta = case["modeled_added_frame_mass_kg"]
        force = sum(x["force_n"] for x in case["axles"])
        assert force == pytest.approx(original_force + delta * 9.80665)
        assert case["total_mass_kg"] == pytest.approx(105750 + delta)
        assert case["force_balance_error_n"] == pytest.approx(0, abs=1e-7)
        assert case["first_moment_balance_error_nm"] == pytest.approx(0, abs=1e-6)
        assert all(
            abs(
                c["added_mass_support_equilibrium"]["first_moment_equilibrium_error_nm"]
            )
            < 1e-7
            for c in case["cars"]
        )


def test_added_mass_bogie_distribution_for_asymmetric_cg_is_static_equilibrium():
    mass = 1000
    cg = 7.1
    r = a.added_mass_support_reactions(mass, cg, [2.1, 14.4])
    left, right = r["reactions_n"]
    assert right == pytest.approx(mass * 9.80665 * (7.1 - 2.1) / (14.4 - 2.1))
    assert left + right == pytest.approx(mass * 9.80665)
    assert left * 2.1 + right * 14.4 == pytest.approx(mass * 9.80665 * cg)
    assert left > right
    assert r["no_uplift"]
    outside = a.added_mass_support_reactions(mass, 1, [2.1, 14.4])
    assert not outside["no_uplift"]
    assert outside["reactions_n"][1] < 0


@pytest.mark.parametrize(
    "mass,cg,supports",
    [(-1, 8.25, [2.1, 14.4]), (1, float("nan"), [2.1, 14.4]), (1, 8.25, [14.4, 2.1])],
)
def test_invalid_added_mass_reaction_inputs(mass, cg, supports):
    with pytest.raises(ValueError):
        a.added_mass_support_reactions(mass, cg, supports)


def test_heavy_frame_mass_matches_independent_section_arithmetic(report):
    side_area = 0.18 * 0.75 - (0.18 - 0.05) * (0.75 - 0.05)
    spine_area = 0.22 * 0.38 - (0.22 - 0.05) * (0.38 - 0.05)
    gross = (2 * side_area * 16 + spine_area * 15.8) * 7850
    assert gross == pytest.approx(14463.625)
    cases = [
        c
        for c in report["cases"]
        if c["referenced_frame_candidate_id"] and "750x25" in c["id"]
    ]
    assert len(cases) == 2
    assert all(
        c["modeled_added_frame_mass_kg"] == pytest.approx(3 * gross) for c in cases
    )
    assert all(c["total_mass_kg"] == pytest.approx(149140.875) for c in cases)


def test_lighter_search_retains_failures_envelope_conflicts_and_actual_inertia(report):
    study = report["lighter_frame_study"]
    assert len(study["candidates"]) == 192
    assert study["termination"]["reason"] == "bounded_domain_exhausted"
    assert study["termination"]["local_stiffness_pass_count"] == 14
    assert study["termination"]["source_compatible_local_stiffness_pass_count"] == 0
    assert any(not c["local_stiffness_screen_passed"] for c in study["candidates"])
    selected = next(
        c for c in study["candidates"] if c["id"] in study["proposed_candidate_ids"]
    )
    h, tf, tw = 0.75, 0.04, 0.008
    flange_area = 0.18 * tf
    independent_side_i = (
        2 * (0.18 * tf**3 / 12 + flange_area * (h / 2 - tf / 2) ** 2)
        + tw * (h - 2 * tf) ** 3 / 12
    )
    assert selected["member_inertias_m4"][0] == pytest.approx(independent_side_i)
    assert selected["proposed_gross_addition_per_car_kg"] == pytest.approx(6122.64832)
    assert selected["nominal_compatible_deflection_m"] < 0.0123
    assert not selected["existing_configuration_compatible"]
    assert (
        next(
            c for c in selected["checks"] if c["id"] == "existing_sill_height_envelope"
        )["status"]
        == "failed"
    )
    assert any(c["status"] == "unknown" for c in selected["checks"])
    assert 2 * sum(selected["member_end_reactions_n"]) == pytest.approx(
        selected["modeled_car_force_n"]
    )
    lighter_case = next(c for c in report["cases"] if "lighter" in c["id"])
    assert lighter_case["total_mass_kg"] == pytest.approx(124117.94496)


def test_source_identity_determinism_and_unclosed_mass_are_explicit(report):
    assert report == a.run()
    assert report["source_sha256"][str(a.TRACE.relative_to(a.ROOT))] == a._digest(
        a.TRACE
    )
    for case in report["cases"]:
        assert case["unclosed_gangway_and_gap_equipment_mass_kg"] is None
        assert case["accepted_replacement_net_steel_mass_kg"] is None
        assert case["vertical_cg_m"] is None
        assert case["mass_is_provisional_model_subtotal"]
        assert not case["accepted_loading"]
