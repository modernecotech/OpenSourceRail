"""Independent stock/load-path/geometry regressions, no field-force surrogate."""
from copy import deepcopy
import math

import pytest

from engineering.factory_examples import models
from engineering.passive_suspension import geometry as g


@pytest.fixture(scope="module")
def samples():
    return {v["sample_id"]: v for v in g.bounded_variants()}


def test_declared_samples_and_no_wayside_excitation(samples):
    assert len(samples) == 9
    for value in samples.values():
        assert value["units_per_car"] == 24
        assert value["packing"]["modules_per_bank"] == 12
        assert value["packing"]["banks_per_car"] == 2
        assert value["installed_mass_kg_per_car"] is None
        assert value["installed_cg_m"] is None
        assert value["unknown_stock"]
        for row in value["unknown_stock"]:
            assert row["mass_kg"] is None and row["cg_m"] is None
        for region in value["regions"]:
            if region["group"] == "guideway":
                assert region["material"] == "steel"
                assert region["Br_y_T"] == region["Br_z_T"] == region["J_x_A_m2"] == 0
                assert "circuit_id" not in region
        assert all(value[k] is False for k in g.FLAGS)


def test_native_stock_recovers_independently_integrated_mass(samples):
    for value in samples.values():
        native = g.native_definition(value)
        train_mass = 0.
        for part in native["parts"]:
            expected_volume = math.prod(part["size_m"])
            assert models.volume(part) == pytest.approx(expected_volume)
            assert part["volume_m3"] == pytest.approx(expected_volume)
            assert part["mass_kg"] == pytest.approx(expected_volume * part["density_kg_m3"])
            assert part["cg_m"] == pytest.approx([a + b/2 for a,b in zip(part["at_m"],part["size_m"])])
            if part["group"] == "train":
                train_mass += part["mass_kg"]
        assert train_mass == pytest.approx(value["stock"]["train_known_mass_kg_per_module"])
        assert value["stock"]["train_known_mass_kg_per_car"] == pytest.approx(train_mass * 24)
        # The emitted native package includes one facing coupon. Its mass is
        # not silently added to or subtracted from the vehicle ledger.
        assert native["modelled_material_mass_kg"] > train_mass
        assert not any("window" in p["id"] for p in native["parts"])


def test_exact_copper_end_turns_and_current_conversion(samples):
    value = samples["C/wide-facing"]
    rho = value["materials"]["copper"]["density_kg_m3"]
    for coil in value["circuits"]:
        stock = [p for p in value["stock_parts"] if p["id"].startswith(coil["id"] + "/turn-")]
        assert len(stock) == 4 * coil["turns"]
        ends = [p for p in stock if "/end-" in p["id"]]
        assert len(ends) == 2 * coil["turns"]
        assert sum(p["mass_kg"] for p in ends) > 0
        volume = sum(math.prod(p["size_m"]) for p in stock)
        assert coil["conductor_length_m"] == pytest.approx(volume/coil["conductor_area_m2"])
        assert coil["copper_mass_kg"] == pytest.approx(volume*rho)
        windows = [r for r in value["regions"] if r.get("circuit_id") == coil["id"]]
        assert len(windows) == 2
        signed = []
        for window in windows:
            a,b,c,d = window["bounds_yz_m"]
            signed.append(window["turns_per_m2"]*(b-a)*(d-c))
        assert sum(signed) == pytest.approx(0., abs=1e-10)
        assert sorted(signed) == pytest.approx([-coil["turns"],coil["turns"]])
        assert coil["current_density_A_m2_per_A"] == pytest.approx(1/coil["conductor_area_m2"])
    assert value["packing"]["physical_module_envelope_x_m"] > value["length_x_m"]


def test_no_positive_field_region_overlap(samples):
    for value in samples.values():
        regions = value["regions"]
        for i,a in enumerate(regions):
            ay0,ay1,az0,az1 = a["bounds_yz_m"]
            for b in regions[i+1:]:
                by0,by1,bz0,bz1 = b["bounds_yz_m"]
                assert min(ay1,by1)-max(ay0,by0) <= 1e-12 or min(az1,bz1)-max(az0,bz0) <= 1e-12, (a["id"],b["id"])


def test_pm_blocks_and_segmented_comparison(samples):
    paired = samples["B/edge-facing"]
    rotated = samples["B/segmented-edge-facing"]
    assert paired["stock"]["train_material_mass_kg_per_module"]["ferrite"] == pytest.approx(rotated["stock"]["train_material_mass_kg_per_module"]["ferrite"])
    for value in (paired,rotated):
        for p in value["stock_parts"]:
            if p["material"] == "ferrite":
                assert p["size_m"][0] <= .10 + 1e-12
                assert p["size_m"][1] <= .06 + 1e-12
                assert math.hypot(p["Br_y_T"],p["Br_z_T"]) == pytest.approx(.45)
    assert any(abs(r["Br_y_T"]) > 0 for r in rotated["regions"])
    assert not any(abs(r["Br_y_T"]) > 0 for r in paired["regions"])
    assert paired["geometry_sha256"] != rotated["geometry_sha256"]


def test_only_facing_mass_varies_with_facing_width(samples):
    edge, wide = samples["B/edge-facing"], samples["B/wide-facing"]
    assert edge["stock"]["train_known_mass_kg_per_module"] == wide["stock"]["train_known_mass_kg_per_module"]
    assert edge["stock"]["guideway_facing_kg_per_route_m"] / wide["stock"]["guideway_facing_kg_per_route_m"] == pytest.approx(.34/.50)
    assert wide["stock"]["guideway_facing_kg_per_beam_span"] == pytest.approx(2*.5*.035*7760*25)
    assert edge["geometry_sha256"] != wide["geometry_sha256"]


def test_short_blocks_share_rigid_frame_error(samples):
    value = samples["B/wide-facing"]
    short = g.candidate("B", {"length_x_m":.5})
    long_result, short_result = g.curve_screen(value,150), g.curve_screen(short,150)
    # Breaking an unchanged 17m frame into shorter magnetic blocks cannot
    # replace its ~100mm sweep with a submillimetre local chord calculation.
    assert long_result["same_rigid_frame_module_error_m"] > .10
    assert short_result["same_rigid_frame_module_error_m"] > .10
    assert short_result["selected_envelope_error_m"] == short_result["same_rigid_frame_module_error_m"]
    assert short_result["selected_envelope_error_m"] > 100*short_result["independent_local_module_error_m"]
    inner_radius = 150-.88-long_result["pole_outer_width_m"]/2
    assert long_result["rigid_frame_chord_sagitta_m"] == pytest.approx(inner_radius-math.sqrt(inner_radius**2-8.5**2))
    assert not long_result["necessary_overlap_pass"]


def test_independent_carrier_needs_translation_and_unqualified_flexure(samples):
    value = samples["D/wide-facing"]
    curve = g.curve_screen(value,150)
    assert curve["independently_required_centre_slide_m"] > .10
    assert curve["independently_required_yaw_rad"] > .05
    assert curve["independent_local_module_error_m"] < .001
    elastic = g.flexure_screen(value, curve["independently_required_yaw_rad"],
                              lateral_translation_m=curve["independently_required_centre_slide_m"])
    assert not elastic["elastic_necessary_pass"]
    assert elastic["geometry_nonlinearity_open"]
    assert elastic["fatigue_qualified"] is False
    assert elastic["multiaxis_load_capacity_n"] is None
    assert elastic["retention_qualified"] is False
    assert all("carrier/leaf" not in r["id"] for r in value["regions"])
    assert len([p for p in value["stock_parts"] if p["id"].startswith("carrier/leaf")]) == 4


def test_pure_bending_known_case_and_scaling(samples):
    value = samples["D/wide-facing"]
    row = g.flexure_screen(value,.05)
    I = .04*.002**3/12
    assert row["per_leaf_rotational_stiffness_n_m_rad"] == pytest.approx(200e9*I/.2)
    assert row["pure_bending_stress_pa"] == pytest.approx(200e9*.002*.05/(2*.2))
    assert row["pinned_weak_axis_euler_load_n_per_leaf"] == pytest.approx(math.pi**2*200e9*I/.2**2)
    assert row["elastic_necessary_pass"]
    assert not row["engineering_accepted"]


def test_attachment_demands_and_capacity_unknown(samples):
    value = samples["B/wide-facing"]
    row = g.attachment_screen(value,15000,lateral_force_n=3000)
    pressure = 15000/(1*.5)
    assert row["plate_bending_stress_pa"] == pytest.approx(.75*pressure*.24**2/.035**2)
    assert row["most_loaded_anchor_tension_n"] == pytest.approx((15000*.5/2+3000*.5*.15/.24)/2)
    assert row["concrete_anchorage_capacity_n"] is None
    assert row["concrete_anchorage_qualified"] is False
    assert row["installed_anchor_mass_kg"] is None
    huge = g.attachment_screen(value,15e6)
    assert not huge["plate_elastic_necessary_pass"]


def test_reference_guidance_and_datum_measurements_remain_unknown(samples):
    a,b = samples["A/wide-facing"],samples["B/wide-facing"]
    assert a["separate_guidance_reference"]["required"]
    assert not a["separate_guidance_reference"]["established"]
    assert any("separate-side-guidance" in r["id"] and r["mass_kg"] is None for r in a["unknown_stock"])
    assert b["separate_guidance_reference"] is None
    datums = g.factory_datums(b)
    assert all(r["measured_m"] is None for r in datums["records"])
    assert not datums["physical_validation"]
    assert g.FHWA_BEARINGS in datums["sources"]


def test_canonical_stock_replacement_does_not_remove_allocations_or_guideway(samples):
    result = g.replacement_mass_comparison(samples["B/wide-facing"])
    assert result["original_module_count_per_car"] == 24
    assert result["original_counted_module_mass_kg"] == pytest.approx(435.9721763217953)
    assert result["removed_counted_stock_kg_per_car"] == pytest.approx(24*435.9721763217953)
    assert result["material_subtotal_aw3_kg_per_car"] == pytest.approx(result["canonical_aw3_kg_per_car"]-24*435.9721763217953+result["added_known_stock_kg_per_car"])
    assert result["removed_guideway_mass_kg"] == 0
    assert result["retained_allocations_unchanged"]
    assert result["installed_aw3_kg_per_car"] is None
    assert result["installed_cg_m"] is None


@pytest.mark.parametrize("params", [{"turns":True},{"length_x_m":float("nan")},
    {"reference_gap_m":0},{"length_x_m":1.3},{"modules_per_bank":30},
    {"temperature_c":40},{"current_A":10},{"flexures_per_module":5},
    {"facing_width_m":1.0}])
def test_invalid_or_operating_geometry_parameters_rejected(params):
    with pytest.raises(ValueError):
        g.candidate("B",params)


def test_tampered_stock_or_facing_rejected(samples):
    for key in ("stock", "region"):
        value = deepcopy(samples["B/wide-facing"])
        if key == "stock":
            value["stock_parts"][0]["mass_kg"] += 1
        else:
            value["regions"][0]["bounds_yz_m"][1] += .01
        with pytest.raises(ValueError,match="identity"):
            g.native_definition(value)
    with pytest.raises(ValueError):
        g.curve_screen(samples["B/wide-facing"],1)
    with pytest.raises(ValueError):
        g.attachment_screen(samples["B/wide-facing"],15000,anchor_rows_y_m=.6)


def test_empirical_material_model_is_not_physical_geometry_identity(samples):
    value = samples["B/wide-facing"]
    changed = deepcopy(value)
    changed["materials"]["ferrite"]["br_temperature_coefficient_per_k"] = -.002
    changed["materials"]["steel"]["curve_basis"] = "Separately declared evaluation hypothesis"
    for r in changed["regions"]:
        r["Br_y_T"] *= .9
        r["Br_z_T"] *= .9
        r["J_x_A_m2"] = 1234 if r.get("circuit_id") else 0
    assert g.physical_definition(changed) == g.physical_definition(value)
    assert changed["physical_geometry_sha256"] == value["physical_geometry_sha256"]
    changed["regions"][0]["bounds_yz_m"][1] += .01
    assert g.physical_definition(changed) != g.physical_definition(value)
