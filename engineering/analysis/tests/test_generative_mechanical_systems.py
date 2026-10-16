"""Independent dimensional, force, energy and coverage controls for LM3 studies."""

import json
import math
from pathlib import Path

import pytest

from engineering.generative_design import mechanical_systems as m


@pytest.fixture(scope="module")
def ctx():
    return m.context()


@pytest.fixture(scope="module")
def report():
    return m.run()


def test_complete_exact_wbs_coverage_and_source_rows(report, ctx):
    required = {k for k in ctx["scope"] if k.startswith(("LM3-FRP-", "BUY-"))}
    assert len(required) == 34
    assert {p["work_package_id"] for p in report["packages"]} == required
    for package in report["packages"]:
        assert package["source_products"]
        for item in package["source_products"]:
            assert item["product_id"] in ctx["products"]
            assert len(item["source_row_sha256"]) == 64
            if item["product_id"] in ctx["pdr"]:
                assert (
                    item["pdr_reference_envelope_mm"]
                    == ctx["pdr"][item["product_id"]]["design_reference_envelope_mm"]
                )
                assert item["pdr_artifact_ids"]
        assert package["package_release_requirements"]
        assert not package["engineering_design_complete"]
        assert not package["physical_release"]


def test_bounded_domains_unique_metrics_reproducibility_and_no_unknown_release(report):
    families = {}
    for package in report["packages"]:
        for investigation in package["investigations"]:
            candidates = investigation["candidates"]
            assert len(candidates) == math.prod(
                len(v) for v in investigation["variable_space"].values()
            )
            assert investigation["termination"]["reason"] == "finite_domain_exhausted"
            families[investigation["id"]] = candidates
            assert not set(investigation["selected_candidate_ids"]) & set(
                investigation["proposed_candidate_ids"]
            )
            for candidate in candidates:
                assert any(x["status"] == "unknown" for x in candidate["checks"])
                assert not candidate["engineering_design_complete"]
                if candidate["id"] in investigation["selected_candidate_ids"]:
                    assert not any(x["status"] == "failed" for x in candidate["checks"])
                    assert candidate["existing_configuration_compatible"]
                if candidate["id"] in investigation["proposed_candidate_ids"]:
                    assert candidate["local_model_screen_feasible"]
                    assert not candidate["existing_configuration_compatible"]
                    assert not candidate["conditional_screen_feasible"]
    ids = {c["id"] for values in families.values() for c in values}
    assert len(ids) == report["summary"]["unique_candidates"]
    assert report == m.run()


def test_front_vs_side_glass_dimensions_and_drain_area(ctx):
    v = dict(
        edge_clearance_m=0.004,
        seal_gap_m=0.009,
        seal_gap_tolerance_m=0.0005,
        drain_diameter_m=0.016,
    )
    front = m.evaluate("glazing", v, ctx)
    side = m.evaluate("side_glazing", v, ctx)
    assert front["metrics"]["assessed_glass_width_m"] == 1.5
    assert side["metrics"]["side_window_zone_widths_m"] == pytest.approx(
        [3.6, 2.9, 3.6]
    )
    assert side["metrics"]["assessed_glass_height_m"] == 0.9
    inflow = 0.05 / 3600 * 3.6 * 0.9
    assert side["metrics"]["rain_inflow_m3_s"] == pytest.approx(inflow)
    assert side["metrics"]["blocked_orifice_capacity_m3_s"] >= inflow
    small = m.evaluate("side_glazing", dict(v, drain_diameter_m=0.008), ctx)
    assert small["metrics"]["blocked_orifice_capacity_m3_s"] == pytest.approx(
        side["metrics"]["blocked_orifice_capacity_m3_s"] / 4
    )


def test_seal_worst_case_interval_and_glass_differential(ctx):
    c = m.evaluate(
        "glazing",
        dict(
            edge_clearance_m=0.004,
            seal_gap_m=0.009,
            seal_gap_tolerance_m=0.0005,
            drain_diameter_m=0.016,
        ),
        ctx,
    )
    assert c["metrics"]["minimum_seal_compression_fraction"] == pytest.approx(
        (12 - 9 - 0.5) / 12
    )
    assert c["metrics"]["maximum_seal_compression_fraction"] == pytest.approx(
        (12 - 9 + 0.5) / 12
    )
    assert c["metrics"]["thermal_half_edge_differential_m"] == pytest.approx(
        (23e-6 - 9e-6) * 60 * 1.78 / 2
    )


def test_lamp_aim_and_extraction_are_geometry_only(ctx):
    c = m.evaluate(
        "lamp",
        dict(
            service_hatch_width_m=0.32,
            aiming_half_travel_m=0.008,
            rear_service_clearance_m=0.08,
        ),
        ctx,
    )
    assert c["metrics"]["beam_offset_at_25m_m"] == pytest.approx(25 * 0.008 / 0.12)
    plate = c["manufacturing_definitions"][0]
    assert plate["width_m"] == pytest.approx(0.32)
    assert plate["height_m"] == pytest.approx(0.205)
    assert all(
        0.02 - 1e-12 <= x <= plate["width_m"] - 0.02 + 1e-12
        for x, y in plate["holes_xy_m"]
    )
    assert any(x["status"] == "unknown" for x in c["checks"])


def test_door_cad_travel_correctly_includes_initial_centre_gap(ctx):
    low = m.evaluate("door", dict(leaf_travel_m=0.5, plug_travel_m=0.03), ctx)
    high = m.evaluate("door", dict(leaf_travel_m=0.692, plug_travel_m=0.06), ctx)
    assert low["metrics"]["clear_opening_m"] == pytest.approx(1.016)
    assert high["metrics"]["clear_opening_m"] == pytest.approx(1.4)
    assert high["metrics"]["leaf_width_m"] == pytest.approx(0.685)
    assert not low["conditional_screen_feasible"]
    assert high["conditional_screen_feasible"]


def test_traction_power_balance_rpm_and_cooling(ctx):
    c = m.evaluate(
        "traction", dict(gear_ratio=6.5, wheel_diameter_m=0.76, speed_km_hr=80), ctx
    )
    metrics = c["metrics"]
    velocity = 80 / 3.6
    assert metrics["motor_speed_rpm"] == pytest.approx(
        velocity / (math.pi * 0.76) * 60 * 6.5
    )
    assert metrics["six_driven_axle_force_n"] * velocity == pytest.approx(
        6 * 250000 * 0.97
    )
    assert metrics["motor_coolant_flow_kg_s"] * 4180 * 10 == pytest.approx(
        250000 / 0.94 - 250000
    )
    assert metrics["mechanical_continuous_power_w"] == 250000


def test_brake_energy_and_original_legacy_mass_convention(ctx):
    assert m.legacy_mass(ctx) == pytest.approx(105750)
    c = m.evaluate(
        "running_unit",
        dict(
            wheel_diameter_m=0.68,
            primary_static_deflection_m=0.02,
            brake_energy_share=1,
        ),
        ctx,
    )
    metrics = c["metrics"]
    assert 12 * metrics["disc_energy_per_stop_j"] == pytest.approx(
        0.5 * 105750 * (80 / 3.6) ** 2
    )
    assert metrics["wheel_wear_radius_change_m"] == pytest.approx(0.04)
    assert 12 * metrics["legacy_equal_axle_static_force_n"] == pytest.approx(
        105750 * 9.81
    )


def test_combined_rigid_rotation_preserves_length_and_zero_state(ctx):
    p = [0.7, -0.4, 1.2]
    q = m.rotation(p, 12, 6, 5)
    assert math.dist([0, 0, 0], q) == pytest.approx(math.dist([0, 0, 0], p))
    zero = m.articulation_demands(ctx, dict(yaw_deg=0, pitch_deg=0, roll_deg=0))
    assert zero["maximum_corner_displacement_m"] == 0
    combined = m.articulation_demands(ctx, dict(yaw_deg=12, pitch_deg=6, roll_deg=5))
    assert combined["maximum_corner_displacement_m"] > 0.3


def test_zero_coupling_gap_not_mislabelled_as_gangway_solution(ctx):
    candidates = m.variants("gangway", ctx)
    zero = [c for c in candidates if c["variables"]["body_gap_m"] == 0]
    assert all(not c["conditional_screen_feasible"] for c in zero)
    assert all(
        next(x for x in c["checks"] if x["id"] == "separate_bodies_module_clearance")[
            "status"
        ]
        == "failed"
        for c in zero
    )
    assert not any(c["conditional_screen_feasible"] for c in candidates)
    repaired = [
        c
        for c in candidates
        if c["local_model_screen_feasible"]
        and not c["existing_configuration_compatible"]
    ]
    assert repaired
    assert all(c["variables"]["body_gap_m"] >= 1.8 for c in repaired)
    chosen = next(c for c in repaired if c["variables"]["body_gap_m"] == 1.8)
    assert chosen["metrics"]["proposed_three_car_length_m"] == pytest.approx(53.1)
    assert chosen["metrics"]["proposed_body_centre_stations_m"] == pytest.approx(
        [0, 18.3, 36.6]
    )


def test_continuous_gangway_bound_contains_interior_angle_rotations(ctx):
    bound = m.continuous_gangway_longitudinal_bound(ctx)
    assert 1.7 < bound < 1.8
    for yaw in [-12, -7, 0, 4, 12]:
        for pitch in [-6, -2, 0, 3, 6]:
            for roll in [-5, -1, 0, 2, 5]:
                metrics = m.articulation_demands(
                    ctx, dict(yaw_deg=yaw, pitch_deg=pitch, roll_deg=roll)
                )
                assert metrics["swept_max_m"][0] - metrics["swept_min_m"][0] <= bound


def test_three_member_frame_preserves_all_car_weight_and_compatibility(ctx):
    c = m.evaluate("chassis_shared", dict(section_height_m=0.75, wall_m=0.025), ctx)
    metrics = c["metrics"]
    assert sum(metrics["member_load_share_fractions"]) == pytest.approx(1)
    assert 2 * sum(metrics["member_end_reactions_n"]) == pytest.approx(
        metrics["conservative_loaded_car_mass_kg"] * 9.81
    )
    assert (
        metrics["conservative_loaded_car_mass_kg"] > metrics["legacy_full_car_mass_kg"]
    )
    curvatures = [
        moment / (200e9 * inertia)
        for moment, inertia in zip(
            metrics["member_midspan_moments_nm"], metrics["member_inertias_m4"]
        )
    ]
    assert max(curvatures) - min(curvatures) < 1e-15
    assert (
        next(x for x in c["checks"] if x["id"] == "research_three_member_stiffness")[
            "status"
        ]
        == "passed"
    )
    assert (
        next(x for x in c["checks"] if x["id"] == "existing_side_sill_envelope")[
            "status"
        ]
        == "failed"
    )
    assert not c["conditional_screen_feasible"]
    assert c["local_model_screen_feasible"]
    assert metrics["source_centre_spine_m"] == pytest.approx([15.8, 0.22, 0.38])


def test_battery_current_tray_fails_and_extension_fits_local_bay(ctx):
    baseline = m.evaluate(
        "hv_hardware",
        dict(
            support_pitch_m=0.5,
            service_hose_diameter_m=0.032,
            tray_length_m=5.4,
            tray_height_m=0.32,
        ),
        ctx,
    )
    revised = m.evaluate(
        "hv_hardware",
        dict(
            support_pitch_m=0.5,
            service_hose_diameter_m=0.032,
            tray_length_m=5.9,
            tray_height_m=0.4,
        ),
        ctx,
    )
    assert baseline["metrics"]["module_dimensions_m"] == pytest.approx(
        [1.45, 0.25, 0.37]
    )
    status = {x["id"]: x["status"] for x in baseline["checks"]}
    assert status["four_modules_tray_length"] == "failed"
    assert status["module_tray_height"] == "failed"
    assert revised["local_model_screen_feasible"]
    assert not revised["existing_configuration_compatible"]
    assert not revised["conditional_screen_feasible"]


def test_service_route_uses_signed_bound_and_new_body_gap(ctx):
    positive = m.articulation_demands(ctx, dict(yaw_deg=12, pitch_deg=6, roll_deg=5))[
        "maximum_corner_displacement_m"
    ]
    opposite = m.articulation_demands(ctx, dict(yaw_deg=12, pitch_deg=6, roll_deg=-5))[
        "maximum_corner_displacement_m"
    ]
    bound = m.continuous_corner_displacement_bound(ctx)
    assert opposite > positive
    assert bound > opposite
    for yaw in [-12, -7, 0, 4, 12]:
        for pitch in [-6, -2, 0, 3, 6]:
            for roll in [-5, -1, 0, 2, 5]:
                assert (
                    m.articulation_demands(
                        ctx, dict(yaw_deg=yaw, pitch_deg=pitch, roll_deg=roll)
                    )["maximum_corner_displacement_m"]
                    <= bound
                )
    feasible = [
        c
        for c in m.variants("service_loop", ctx)
        if c["local_model_screen_feasible"]
        and not c["existing_configuration_compatible"]
    ]
    assert feasible
    assert all(c["variables"]["body_gap_m"] >= 1.8 for c in feasible)
    assert all(not c["conditional_screen_feasible"] for c in feasible)
    assert all(
        c["metrics"]["developed_service_length_m"]
        >= c["variables"]["body_gap_m"] + bound
        for c in feasible
    )


@pytest.mark.parametrize("family", ["articulation", "gangway", "service_loop"])
def test_new_intercar_gaps_are_only_incompatible_proposals(family, ctx):
    cases = m.variants(family, ctx)
    proposals = [c for c in cases if c["local_model_screen_feasible"]]
    assert proposals
    for candidate in cases:
        if candidate["variables"]["body_gap_m"] != ctx["c"]["COUPLING_GAP_MM"] / 1000:
            assert not candidate["existing_configuration_compatible"]
            assert not candidate["conditional_screen_feasible"]
            assert (
                next(
                    x
                    for x in candidate["checks"]
                    if x["id"] == "existing_intercar_spacing"
                )["status"]
                == "failed"
            )


def test_known_bogie_and_glazing_conflicts_cannot_pass_as_compatible(ctx):
    bogie = m.evaluate(
        "bogie_frame",
        dict(frame_width_m=2.4, vertical_motion_m=0.03, frame_length_m=3.5),
        ctx,
    )
    assert (
        next(x for x in bogie["checks"] if x["id"] == "pdr_frame_envelope_fit")[
            "status"
        ]
        == "failed"
    )
    compact = m.evaluate(
        "bogie_frame",
        dict(frame_width_m=2.4, vertical_motion_m=0.03, frame_length_m=3.4),
        ctx,
    )
    assert compact["local_model_screen_feasible"]
    assert not compact["existing_configuration_compatible"]
    assert not compact["conditional_screen_feasible"]
    for family in ["glazing", "side_glazing"]:
        cases = m.variants(family, ctx)
        assert any(c["local_model_screen_feasible"] for c in cases)
        assert all(not c["conditional_screen_feasible"] for c in cases)


def test_voltage_drop_wire_area_scaling_and_lifting_force(ctx):
    v = dict(wire_area_mm2=1.5, branch_current_a=10)
    small = m.evaluate("lv_harness", v, ctx)
    large = m.evaluate("lv_harness", dict(v, wire_area_mm2=6), ctx)
    assert small["metrics"]["drop_v"] == pytest.approx(4 * large["metrics"]["drop_v"])
    assert not small["conditional_screen_feasible"]
    lift = m.evaluate(
        "lifting",
        dict(effective_jacks=4, dynamic_multiplier=1, load_imbalance_multiplier=1),
        ctx,
    )
    assert lift["metrics"]["nominal_load_each_effective_jack_n"] * 4 == pytest.approx(
        105750 * 9.81 / 3
    )


def test_source_discrepancies_are_retained_and_artifacts_exist(report, tmp_path):
    assert len(report["source_discrepancies"]) == 5
    paths = m.write_artifacts(report, tmp_path)
    assert all(p.is_file() and p.stat().st_size > 0 for p in paths)
    assert len(paths) > 68
    lamp = tmp_path / "LM3-FRP-040/lamp-plate.svg"
    assert "UNRELEASED RESEARCH" in lamp.read_text()
    drill = tmp_path / "LM3-FRP-070/service-rail-drill.csv"
    assert drill.read_text().startswith("x_m,y_m,hole_diameter_m")
    retained = json.loads((tmp_path / "report.json").read_text())
    assert not retained["physical_release"]
    assert not retained["engineering_design_complete"]
    before = (tmp_path / "report.json").read_bytes()
    assert m.write_artifacts(report, tmp_path) == paths
    assert (tmp_path / "report.json").read_bytes() == before


def test_ast_constant_reader_does_not_execute_source(tmp_path):
    source = tmp_path / "constants.py"
    marker = tmp_path / "executed"
    source.write_text(
        "A=2\nB=A*3\nopen(" + repr(str(marker)) + ",'w').write('executed')\n"
    )
    assert m.constants([source]) == {"A": 2, "B": 6}
    assert not marker.exists()
