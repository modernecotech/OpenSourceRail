"""Independent quantity and plate-domain regressions for comfort glazing."""
from copy import deepcopy
import math

import pytest

from engineering.comfort_options import glazing as g


@pytest.fixture(scope="module")
def candidates():
    return {n: g.options(n) for n in (2, 3, 4)}


def test_exact_retained_glass_reference_and_door_ownership(candidates):
    for n, rows in candidates.items():
        ref = rows[0]
        area, perimeter = 24 + n, 56 + 6 * n
        glass = area * (0.006 * 2500 + 0.00076 * 1070)
        retention = perimeter * (0.020 * 0.003 * 2700 + 0.00008 * 1200 + 0.012 * 0.003 * 1200)
        assert ref["known_sheet_mass_kg"] == pytest.approx(glass)
        assert ref["counted_material_mass_kg"] == pytest.approx(glass + retention)
        assert ref["total_area_m2"] == area
        assert ref["door_window_count"] == 2 * n
        assert ref["door_area_m2"] == n
        assert ref["retention_perimeter_m"] == perimeter
        assert ref["counted_stock_saving_vs_same_door_count_glass_kg"] == pytest.approx(0)
    assert candidates[4][0]["counted_material_mass_kg"] == pytest.approx(466.8656)
    # Door removal changes one square metre of sheet and six metres of framing.
    assert candidates[4][0]["counted_material_mass_kg"] - candidates[2][0]["counted_material_mass_kg"] == pytest.approx(
        2 * (0.006 * 2500 + 0.00076 * 1070) + 12 * (0.00006 * 2700 + 0.00008 * 1200 + 0.000036 * 1200))


def test_all_panes_cover_gross_area_without_door_double_count(candidates):
    for n, rows in candidates.items():
        assert len(rows) == 11
        for c in rows:
            a, b = c["fixed_window_size_m"]
            da, db = c["door_window_size_m"]
            assert c["fixed_window_count"] * a * b == pytest.approx(24)
            assert c["door_window_count"] * da * db == pytest.approx(n)
            assert c["total_area_m2"] == c["fixed_area_m2"] + c["door_area_m2"]
            assert c["counted_material_mass_kg"] == pytest.approx(math.fsum(
                p["volume_m3_each"] * p["density_kg_m3"] * p["quantity"] for p in c["stock_parts"]))


def test_segmentation_counts_material_and_supports(candidates):
    rows = [c for c in candidates[2] if c["material"] == "coated-polycarbonate" and c["sheet_thickness_m"] == 0.008]
    full, halves, quarters = rows
    assert [r["fixed_window_count"] for r in rows] == [8, 16, 32]
    assert [r["retention_perimeter_m"] for r in rows] == [68, 92, 124]
    section_area = 0.08 * 0.04 - 0.074 * 0.034
    half_stock = {p["id"]: p for p in halves["stock_parts"]}
    quarter_stock = {p["id"]: p for p in quarters["stock_parts"]}
    assert half_stock["glazing/mullion-vertical"]["total_mass_kg"] == pytest.approx(12 * section_area * 2700)
    assert quarter_stock["glazing/mullion-horizontal"]["total_mass_kg"] == pytest.approx(16 * section_area * 2700)
    assert full["known_sheet_mass_kg"] == halves["known_sheet_mass_kg"] == quarters["known_sheet_mass_kg"]
    assert full["counted_material_mass_kg"] < halves["counted_material_mass_kg"] < quarters["counted_material_mass_kg"]


def test_equal_stiffness_can_remove_density_saving(candidates):
    eq = g.equal_stiffness_pc_thickness_bounds_m()
    assert 0.011 < eq["uncoupled_glass_equivalent"] < 0.013
    assert 0.019 < eq["fully_coupled_glass_equivalent"] < 0.022
    bounds = g.laminate_rigidity_bounds()
    for key, target in (("uncoupled_glass_equivalent", bounds["uncoupled_Nm"]),
                        ("fully_coupled_glass_equivalent", bounds["fully_coupled_Nm"])):
        t = eq[key]
        assert g.PC_E_PA * t**3 / (12 * (1 - g.PC_NU**2)) == pytest.approx(target)
    glass = candidates[4][0]
    thick_segmented = candidates[4][-1]
    assert thick_segmented["counted_material_mass_kg"] > glass["counted_material_mass_kg"]
    assert thick_segmented["counted_stock_saving_vs_same_door_count_glass_kg"] < 0


def test_navier_independent_square_coefficient_scaling_and_rotation():
    first = g.plate_center(1, 1, 1, 1, 0.3, odd_terms=1)
    assert first["centre_deflection_m"] == pytest.approx(4 / math.pi**6)
    fine = g.plate_center(1, 1, 1, 1, 0.3, odd_terms=61)
    assert fine["centre_deflection_m"] == pytest.approx(0.004062352660675, rel=1e-7)
    r = g.plate_center(2, 1.5, 500, 100, 0.38)
    rotated = g.plate_center(1.5, 2, 500, 100, 0.38)
    scaled = g.plate_center(4, 3, 1000, 200, 0.38)
    assert rotated["centre_deflection_m"] == pytest.approx(r["centre_deflection_m"])
    assert rotated["centre_moment_x_Nm_per_m"] == pytest.approx(r["centre_moment_y_Nm_per_m"])
    assert scaled["centre_deflection_m"] == pytest.approx(16 * r["centre_deflection_m"])


def test_large_linear_deflection_remains_out_of_domain(candidates):
    thin_full = candidates[2][1]
    f = thin_full["evaluation"]["fixtures"][-1]["fixed_panel"]
    assert f["w_over_thickness"] > 0.5
    assert f["numerical_validity"] == "outside_small_deflection_domain"
    assert f["declared_target_5mm_screen"] == "unknown"
    assert f["declared_target_25mm_screen"] == "unknown"
    # A converged series does not make a large-displacement model valid.
    assert f["series_deflection_relative_change"] < 1e-5
    assert thin_full["evaluation"]["engineering_screen"] == "unknown"


def test_smallest_thick_panel_is_a_valid_fixture_with_counted_support_not_acceptance(candidates):
    small = candidates[2][-1]
    assert small["fixed_window_count"] == 48
    assert small["fixed_window_size_m"] == [1.0, 0.5]
    support = {s["id"]: s for s in small["stock_parts"]}
    assert support["glazing/mullion-horizontal"]["quantity"] == 32
    fixture = small["evaluation"]["fixtures"][-1]
    assert fixture["fixed_panel"]["small_deflection_domain"]
    assert fixture["fixed_panel"]["declared_target_5mm_screen"] == "pass"
    assert all(m["assembled_grid_screen"] == "unknown" for m in fixture["mullions"])
    assert small["counted_stock_saving_vs_same_door_count_glass_kg"] < 0
    assert small["evaluation"]["engineering_screen"] == "unknown"
    assert not small["physical_accepted"]


def test_glass_laminate_bounds_retained_and_no_monolithic_strength_claim(candidates):
    fixtures = candidates[2][0]["evaluation"]["fixtures"]
    uncoupled, coupled = fixtures[:2]
    assert uncoupled["model"] == "uncoupled"
    assert coupled["model"] == "fully_coupled"
    assert uncoupled["fixed_panel"]["centre_deflection_m"] > coupled["fixed_panel"]["centre_deflection_m"]
    assert all(f["fixed_panel"]["centre_stress_Pa_if_monolithic"] is None for f in fixtures)


def test_thermal_properties_and_complete_installed_inventory_stay_unknown(candidates):
    for rows in candidates.values():
        for c in rows:
            assert c["actual_solar_factor_g"] is None and c["actual_U_W_m2K"] is None
            assert c["solar_factor_g"] is None and c["U_W_m2K"] is None
            assert c["installed_mass_kg"] is None and c["installed_cost"] is None
            assert c["unknown_installed_inventory"]
            assert all(p["mass_kg"] is None for p in c["unknown_installed_inventory"])
            assert len(c["thermal_sensitivities"]) == 3
            assert not c["physical_accepted"] and not c["manufacturing_release"]
            assert not c["manufacturer_evidence"]["published_test_claim_transferred_to_this_assembly"]
    pc = candidates[2][1]
    assert pc["evaluation"]["thermal_expansion"]["fixed_panel_free_expansion_m"][0] == pytest.approx(0.0081)
    assert pc["evaluation"]["thermal_expansion"]["actual_retention_travel_m"] is None


def test_distinct_physical_and_evaluation_identities_and_tamper_rejection(candidates):
    ids = [r["physical_definition_id"] for rows in candidates.values() for r in rows]
    assert len(set(ids)) == 33
    ref = candidates[2][1]
    assert g.validate(ref, doors_total=2) == ref
    with pytest.raises(ValueError, match="doors_total differ"):
        g.validate(ref, doors_total=3)
    for path in ("counted_material_mass_kg", "total_area_m2", "evaluation_id"):
        changed = deepcopy(ref)
        changed[path] = 0
        with pytest.raises(ValueError, match="changed"):
            g.validate(changed)
    changed = deepcopy(ref)
    changed["stock_parts"][0]["thickness_m"] = 0.001
    with pytest.raises(ValueError):
        g.validate(changed)
    low, high = g.evaluate(ref, [500]), g.evaluate(ref, [1500])
    assert g.evaluate(ref)["evaluation_id"] == ref["evaluation_id"]
    assert low["physical_definition_id"] == high["physical_definition_id"] == ref["glazing_id"]
    assert low["evaluation_id"] != high["evaluation_id"]


def test_fresh_records_and_invalid_definition_inputs():
    a = g.options(2)
    a[1]["stock_parts"][0]["total_mass_kg"] = -1
    assert g.options(2)[1]["stock_parts"][0]["total_mass_kg"] > 0
    for n in (True, 1, 5, 2.0, "2"):
        with pytest.raises(ValueError):
            g.options(n)
    for pressure in (0, -1, float("nan"), True):
        with pytest.raises(ValueError):
            g.plate_center(1, 1, pressure, 1)
    with pytest.raises(ValueError):
        g.plate_center(1, 1, 500, 1, odd_terms=0)
