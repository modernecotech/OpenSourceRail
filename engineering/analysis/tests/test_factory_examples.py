"""Independent analytical controls and adverse factory development cases."""

from copy import deepcopy
import json
import shutil

import pytest

from engineering.factory_examples import build, models


@pytest.fixture
def basis():
    return json.loads((build.PACKAGE / "data/basis.json").read_text())["assumptions"]


@pytest.fixture
def equipment():
    rows = json.loads((build.PACKAGE / "data/equipment.json").read_text())["equipment"]
    return {e["id"]: e for e in rows}


def test_central_point_load_matches_closed_form():
    L, P, E, I = 4, 1000, 200e9, 2e-5
    r = models.point_beam(L, [(L / 2, P)], E, I)
    assert r["left_reaction_n"] == pytest.approx(P / 2)
    assert r["right_reaction_n"] == pytest.approx(P / 2)
    assert r["maximum_abs_moment_nm"] == pytest.approx(P * L / 4)
    assert r["maximum_abs_deflection_m"] == pytest.approx(P * L**3 / (48 * E * I))


def test_distributed_load_limit_matches_independent_udl_solution():
    L, q, E, I = 5, 2000, 210e9, 1e-5
    n = 1000
    r = models.point_beam(L, [((i + 0.5) * L / n, q * L / n) for i in range(n)], E, I)
    assert r["maximum_abs_moment_nm"] == pytest.approx(q * L * L / 8, rel=1e-5)
    assert r["maximum_abs_deflection_m"] == pytest.approx(
        5 * q * L**4 / (384 * E * I), rel=1e-5
    )


@pytest.mark.parametrize(
    "span,loads", [(0, [(0, 1)]), (1, [(2, 1)]), (1, [(0.5, float("nan"))])]
)
def test_impossible_beams_rejected(span, loads):
    with pytest.raises(ValueError):
        models.point_beam(span, loads, 200e9, 1e-5)


def test_fixture_equilibrium_stock_and_no_false_release(basis):
    f = models.fixture(basis)
    R = f["vertical_reactions_n"]
    assert sum(R) == pytest.approx(500 * 9.80665 * 1.5)
    assert R == pytest.approx([sum(R) / 4, sum(R) / 4, sum(R) / 2])
    assert f["restraint"]["constraint_rank"] == 6
    stock = sum(models.volume(p) for p in f["parts"] if p["kind"] == "tube")
    assert stock == pytest.approx(
        (2 * 1.6 + 4 * 0.9 + 4 * 0.68) * (0.1 * 0.05 - 0.09 * 0.04)
    )
    assert models.bounds(f["parts"]) == pytest.approx(
        [-0.85, -0.555, 0, 0.85, 0.555, 1.05]
    )
    assert f["released"] is False
    assert f["restraint"]["fixture_released"] is False


def test_eccentric_payload_records_locator_lift_off(basis):
    basis["fixture_payload_cg_xy_m"] = [0.7, 0.2]
    f = models.fixture(basis)
    assert min(f["vertical_reactions_n"]) < 0
    assert f["payload_cg_within_support_triangle"] is False
    assert f["released"] is False


def test_cross_section_against_independent_strip_integration(basis):
    r = models.civil(basis)
    n = 10000
    dz = 1.155 / n
    strips = [
        ((i + 0.5) * dz, (2.9 if (i + 0.5) * dz >= 0.935 else 0.6) * dz)
        for i in range(n)
    ]
    A = sum(area for _, area in strips)
    zbar = sum(z * area for z, area in strips) / A
    I = sum((z - zbar) ** 2 * area for z, area in strips)
    assert r["section"]["area_m2"] == pytest.approx(A, rel=0.001)
    assert r["section"]["centroid_z_m"] == pytest.approx(zbar, rel=0.001)
    assert r["section"]["inertia_x_m4"] == pytest.approx(I, rel=0.001)


def test_civil_mass_reconciles_nonoverlapping_solid_fill(basis):
    c = models.civil(basis)
    for s in c["scenarios"]:
        bare = sum(
            models.volume(p) for p in models.pi_parts(s["span_m"], developed=False)
        )
        developed = sum(models.volume(p) for p in models.pi_parts(s["span_m"]))
        assert bare == pytest.approx(s["bare_volume_m3"])
        assert developed * 2500 == pytest.approx(s["developed_mass_kg"])
        assert developed - bare == pytest.approx(2.36555)
        assert s["railway_live_load_result"] is None
        assert s["eighty_tonne_screen"] is False
    assert c["scenarios"][1]["handling_equivalent_kg"] == pytest.approx(103564.21875)
    assert c["bed_screen"]["full_25m_euler_ratio"] > 1
    assert c["bed_screen"]["brace_capacity_established"] is False


def test_prestress_shortening_satisfies_transfer_equilibrium(basis):
    c = models.civil(basis)
    A, I = c["section"]["area_m2"], c["section"]["inertia_x_m4"]
    groups = c["prestress_hypothesis"]["group_inputs"]
    for s in c["scenarios"]:
        after = [
            g["pretransfer_stress_pa"] - loss
            for g, loss in zip(groups, s["elastic_shortening_loss_pa"])
        ]
        force = sum(g["metallic_area_m2"] * stress for g, stress in zip(groups, after))
        moment = sum(
            g["metallic_area_m2"] * stress * g["eccentricity_m"]
            for g, stress in zip(groups, after)
        )
        for g, loss in zip(groups, s["elastic_shortening_loss_pa"]):
            strain = (
                force / A
                + g["eccentricity_m"] * (moment - s["bare_dead_moment_nm"]) / I
            ) / basis["concrete_transfer_modulus_pa"]
            assert loss == pytest.approx(g["steel_modulus_pa"] * strain)
        # Independent integration of the reported linear concrete stress field.
        top = s["transfer_fiber_stress"]["top_pa"]
        bottom = s["transfer_fiber_stress"]["soffit_pa"]
        gradient = (top - bottom) / 1.155
        rectangles = [(2.9, 0.22, 1.045), (0.3, 0.935, 0.4675), (0.3, 0.935, 0.4675)]
        integrated = sum(b * h * (bottom + gradient * z) for b, h, z in rectangles)
        assert integrated == pytest.approx(force)
        assert s["transfer_fiber_stress"]["allowable_stress_pa"] is None


def test_pilot_capacity_is_not_programme_capacity(basis):
    c = models.capacity(basis)
    assert c["planning_accepted_beams_per_working_day"] == pytest.approx(1.615)
    assert c["positions_required_at_same_assumptions"] == 134
    assert c["measured_production"] is False
    basis["bed_availability"] = 0
    with pytest.raises(ValueError):
        models.capacity(basis)


def test_floor_reservations_detect_aisle_overlap_and_boundary():
    layouts = models.layouts(build.ROOT)
    for key in ("vehicle", "precast"):
        assert models.check_layout(layouts[key])["valid"]
    bad = deepcopy(layouts["vehicle"])
    bad["zones"][2]["rect_m"] = [1, 13, 16, 10]
    assert not models.check_layout(bad)["valid"]
    bad["zones"][2]["rect_m"] = [140, 45, 16, 10]
    assert any("outside" in e for e in models.check_layout(bad)["errors"])


def test_equipment_fit_changes_with_actual_work_envelope(basis, equipment):
    f = models.fixture(basis)
    fit = models.capability(equipment, f)
    assert fit["plate_mazak_envelope_screen"]
    assert fit["plate_cmm_envelope_screen"]
    assert not fit["full_fixture_cmm_envelope_screen"]
    equipment["mazak-cv5-500"]["published"]["workpiece_diameter_m"] = 0.1
    equipment["aberlink-axiom-900"]["published"]["measuring_range_m"] = [0.1, 0.1, 0.1]
    fit = models.capability(equipment, f)
    assert not fit["plate_mazak_envelope_screen"]
    assert not fit["plate_cmm_envelope_screen"]


def test_machine_does_not_fit_when_actual_footprint_grows(equipment):
    layout = models.layouts(build.ROOT)["vehicle"]
    equipment["mazak-cv5-500"]["published"]["dimensions_xy_m"] = [20, 20]
    with pytest.raises(ValueError, match="doesn't fit"):
        models.factory_scene(layout, equipment, roof_load_pa=600, slab_thickness=0.25)


def test_unknown_costs_utilities_ground_and_release_remain_unknown():
    outputs, _ = build.make_outputs()
    r = json.loads(outputs["report.json"])
    assert r["costs"]["installed_capex_gbp"] is None
    assert r["costs"]["complete"] is False
    assert r["building_screen"]["required_pad_area_m2"] is None
    mazak = next(row for row in r["utilities"] if row["id"] == "mazak-cv5-500")
    assert mazak["input_kva_max"] is None
    assert r["physical_release"] is False
    assert r["supplier_contacted"] is False


def test_all_published_equipment_facts_keep_source_and_assumptions(equipment):
    assert len(equipment) == 14
    for e in equipment.values():
        assert e["sources"] and e["source_locator"] and e["origin"] and e["unknown"]
        assert all(s.startswith("https://") for s in e["sources"])
    assert "requested_capacity_kg" not in equipment["street-open-winch"]["published"]
    assert "height_m" not in equipment["mazak-cv5-500"]["published"]


def test_text_artifacts_reproduce():
    first, models_a = build.make_outputs()
    second, models_b = build.make_outputs()
    assert first == second
    assert models_a == models_b
    for name, content in first.items():
        assert (build.DEFAULT / name).read_text() == content, name


def test_stock_conservation_and_short_stock_rejection(basis):
    f = models.fixture(basis)
    plan = models.cutting_plan(f)
    assert plan["stock_count"] == 2
    assert plan["finished_length_m"] == pytest.approx(9.52)
    assert 12 == pytest.approx(
        plan["finished_length_m"]
        + plan["kerf_total_m"]
        + plan["trim_total_m"]
        + plan["residual_total_m"]
    )
    assert plan["residual_total_m"] == pytest.approx(2.37)
    with pytest.raises(ValueError, match="stock too short"):
        models.cutting_plan(f, stock_length=1)


def test_retained_native_artifacts_match_current_sources(monkeypatch):
    monkeypatch.setattr("sys.argv", ["factory-example-check", "--check"])
    build.main()


def test_retained_native_file_tampering_is_detected(tmp_path, monkeypatch):
    output = tmp_path / "examples"
    shutil.copytree(
        build.DEFAULT, output, ignore=shutil.ignore_patterns("*.step", "*.FCBak")
    )
    path = output / "fixture/model.FCStd"
    path.write_bytes(path.read_bytes() + b"tampered")
    monkeypatch.setattr(
        "sys.argv", ["factory-example-check", "--check", "--output", str(output)]
    )
    with pytest.raises(SystemExit, match="native file mismatch"):
        build.main()
