"""Independent material-account, sandwich-strip and component-scope checks."""
from copy import deepcopy
import math
import json
from pathlib import Path
import shutil

import pytest

from engineering.research_test_support import evidence_root
from engineering.comfort_options import envelope as e

EVIDENCE_ROOT = evidence_root(Path(__file__).resolve().parents[3],
    required=('engineering/ferrite_maglev/data/candidate-retained-body-stock.json',),
    sources=('engineering/comfort_options/envelope.py',))


@pytest.fixture(scope="module")
def rows():
    return e.options(root=EVIDENCE_ROOT)


def test_exact_retained_floor_roof_and_replacement_ownership(rows):
    by_id = {r["id"]: r for r in rows}
    floor = by_id["floor/retained/2.25mm/core-100"]
    roof = by_id["roof/retained/2mm/core-80"]
    assert floor["counted_mass_kg"] == pytest.approx(17 * 2.65 * (2 * 0.00225 * 1900 + 0.06 * 100 + 0.001 * 1000))
    assert floor["counted_mass_kg"] == pytest.approx(700.5275)
    assert roof["counted_mass_kg"] == pytest.approx(518.075)
    for r in rows:
        assert r["mass_basis"] == "per car " + r["role"] + " assembly"
        assert len(r["replacement_scope_part_ids"]) == 4
        assert all(x.startswith("panel/" + r["role"] + "/") for x in r["replacement_scope_part_ids"])
        for f in r["frame_context"]["aluminium_frame_comparisons"]:
            assert not set(f["ancestor_part_ids"]) & set(r["replacement_scope_part_ids"])
        assert r["conditional_counted_stock_saving_kg"] == pytest.approx(
            r["retained_panel_counted_material_mass_kg"] - r["counted_mass_kg"])


def test_tiled_stock_closes_and_counts_edge_bond_inserts_and_fasteners(rows):
    for r in rows:
        assert r["counted_material_mass_kg"] == pytest.approx(math.fsum(
            s["volume_m3_each"] * s["quantity"] * s["density_kg_m3"] for s in r["stock_parts"]))
        if r["physical_definition"]["skin_kind"] == "retained":
            continue
        d = r["physical_definition"]
        assert d["panel_count"] == 24
        assert math.prod(d["panel_size_m"]) * d["panel_count"] == pytest.approx(45.05)
        s = {x["id"]: x for x in r["stock_parts"]}
        core = s["core/trimmed-foam"]
        assert core["volume_m3_each"] + core["displaced_edge_wall_volume_m3_each"] + core["displaced_insert_volume_m3_each"] == pytest.approx(
            math.prod(d["panel_size_m"]) * d["core_m"])
        assert s["edge/GFRP-vertical-ring"]["total_mass_kg"] > 0
        assert s["edge/GFRP-lap-rings"]["quantity"] == 48
        assert s["bond/edge-lap"]["total_mass_kg"] > 0
        assert s["attachment/aluminium-sleeve"]["quantity"] == 96
        assert s["attachment/steel-load-spreader"]["quantity"] == 192
        assert s["attachment/M6-shank"]["quantity"] == 96
        assert s["attachment/M6-head-nut-envelope"]["quantity"] == 96


def test_independent_face_integral_and_bending_shear_scaling():
    t, c, E, Gc = 0.0015, 0.06, 22e9, 23e6
    a = e.sandwich_strip(t, c, E, Gc, 1, 5000)
    assert a["face_second_moment_m4"] == pytest.approx(((c + 2 * t)**3 - c**3) / 12)
    assert a["core_peak_shear_Pa"] == pytest.approx((5000 / 2) / c)
    assert a["face_EA_N"] == pytest.approx(2 * t * E)
    longer = e.sandwich_strip(t, c, E, Gc, 2, 5000)
    assert longer["bending_deflection_m"] == pytest.approx(16 * a["bending_deflection_m"])
    assert longer["shear_deflection_m"] == pytest.approx(4 * a["shear_deflection_m"])
    double_pressure = e.sandwich_strip(t, c, E, Gc, 1, 10000)
    assert double_pressure["total_deflection_m"] == pytest.approx(2 * a["total_deflection_m"])
    stiff_core = e.sandwich_strip(t, c, E, 2 * Gc, 1, 5000)
    assert stiff_core["bending_deflection_m"] == a["bending_deflection_m"]
    assert stiff_core["shear_deflection_m"] == pytest.approx(a["shear_deflection_m"] / 2)


def test_mass_reduction_does_not_hide_global_stiffness_loss(rows):
    light = next(r for r in rows if r["id"] == "floor/glass-epoxy/1mm/core-80")
    assert light["conditional_counted_stock_saving_kg"] > 200
    assert light["evaluation"]["global_stiffness_comparison"]["face_EA_ratio_to_retained"] == pytest.approx(22 * 1 / (20 * 2.25))
    assert light["evaluation"]["global_stiffness_comparison"]["continuous_section_stiffness_necessary_screen"] == "fail"
    assert light["necessary_screen"] == "fail"
    al = next(r for r in rows if r["id"] == "floor/aluminium/0.9mm/core-80")
    assert al["necessary_screen"] == "pass"
    assert al["conditional_counted_stock_saving_kg"] > 0
    assert not al["global_body_qualified"]
    assert al["evaluation"]["engineering_screen"] == "unknown"


def test_nominal_roof_deflection_failure_retains_reference_failure(rows):
    roof = [r for r in rows[:18] if r["role"] == "roof"]
    assert all(r["necessary_screen"] == "fail" for r in roof)
    ref = next(r for r in roof if r["physical_definition"]["skin_kind"] == "retained")
    f = next(f for f in ref["evaluation"]["local_fixtures"] if f["span_m"] == 2.125 and f["imposed_pressure_Pa"] == 1500)
    assert f["deflection_necessary_screen"] == "fail"
    assert f["numerical_validity"] == "valid_linear_fixture"


def test_large_deflection_and_point_loads_do_not_claim_qualification(rows):
    for r in rows:
        global_strip = r["evaluation"]["global_stiffness_comparison"]["panel_alone_17m_strip"]
        assert global_strip["numerical_validity"] == "outside_small_deflection_domain"
        assert global_strip["deflection_necessary_screen"] == "unknown"
        for f in r["evaluation"]["local_fixtures"]:
            assert f["face_strength_screen"] == "unknown"
            assert f["face_wrinkling_bond_point_load_and_fixing_screen"] == "unknown"
            assert f["core_shear_comparison_allowable_Pa"] == r["core_properties"]["shear_strength_min_Pa"] / 2
        assert r["evaluation"]["thermal"]["complete_assembly_U_W_m2K"] is None
        assert r["evaluation"]["thermal"]["actual_core_temperature_C"] is None
        assert r["evaluation"]["thermal"]["material_continuous_core_temperature_limit_C"] == 70


def test_frame_reactions_and_source_parts_are_preserved(rows):
    frames = rows[0]["frame_context"]["aluminium_frame_comparisons"]
    assert [f["fixed_magnetic_force_N_per_module"] for f in frames] == [40000, 70000]
    assert [f["counted_material_mass_kg"] for f in frames] == pytest.approx([1220.8307160380168, 1367.8596334100168])
    assert all(f["ancestor_frame_counted_kg"] == pytest.approx(1224.0216304494938) for f in frames)
    assert all(len(f["ancestor_part_ids"]) == 260 and len(f["generated_stock_ids"]) == 278 for f in frames)
    assert all(f["engineering_member_count"] == 65 for f in frames)
    for r in rows:
        assert not r["frame_context"]["lower_passenger_count_reduces_fixed_magnetic_design_load"]
        assert r["compatible_complete_body_record_id"] is None
        assert not r["applied_to_current_parent"] and not r["mass_saving_credited_to_current_parent"]
        assert r["installed_mass_kg"] is None
        assert all(x["mass_kg"] is None for x in r["unknown_installed_inventory"])


def test_source_and_identity_contract_rejects_quantity_or_mass_credit_edits(rows):
    assert len(rows) == 22
    assert len({r["physical_definition_id"] for r in rows}) == 22
    for r in rows:
        assert e.validate(r, root=EVIDENCE_ROOT) == r
    for key, value in (("counted_mass_kg", 0), ("applied_to_current_parent", True),
                       ("mass_saving_credited_to_current_parent", True),
                       ("evaluation_id", "forged")):
        changed = deepcopy(rows[1])
        changed[key] = value
        with pytest.raises(ValueError, match="changed"):
            e.validate(changed, root=EVIDENCE_ROOT)
    changed = deepcopy(rows[1])
    changed["stock_parts"][0]["total_mass_kg"] = 0
    with pytest.raises(ValueError):
        e.validate(changed, root=EVIDENCE_ROOT)


def test_no_cross_tree_evaluator_mix(tmp_path):
    for name in e.source_inputs(EVIDENCE_ROOT):
        if name == "engineering/comfort_options/envelope.py":
            continue
        dst = tmp_path / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(EVIDENCE_ROOT / name, dst)
    target = tmp_path / "engineering/halbach_scaling/vehicles.py"
    target.write_text(target.read_text() + "\n# changed evaluator\n")
    with pytest.raises(ValueError, match="dependency differ"):
        e.source_inputs(tmp_path)


def test_identical_copied_sources_produce_portable_public_records(rows, tmp_path):
    inputs = e.source_inputs(EVIDENCE_ROOT)
    for name in inputs:
        dst = tmp_path / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        source = Path(e.__file__) if name == "engineering/comfort_options/envelope.py" else EVIDENCE_ROOT / name
        shutil.copyfile(source, dst)
    copied = e.options(root=tmp_path)
    assert copied == rows
    assert e.validate(copied[1], root=tmp_path) == rows[1]
    for r in copied:
        assert "source_root" not in r
        assert r["source_sha256"] == r["source_inputs"]
    encoded = json.dumps(copied)
    assert str(EVIDENCE_ROOT) not in encoded
    assert str(e.ROOT) not in encoded
    assert str(tmp_path) not in encoded


def test_second_iteration_preserves_original_physical_ids_and_numerical_fixtures(rows):
    # Retained from the independently executed first iteration at d4f459555c.
    assert e._hash([r["physical_definition_id"] for r in rows[:18]]) == "5001cb411a2410c597c814053f6d5dd83960804b1e62c7af239c867c54da899b"
    assert e._hash([r["evaluation"] for r in rows[:18]]) == "d1582280a9675aa5dc63f33cda80d49e73dd844d60d0b527a1e88514a6da0080"


def test_new_roof_rails_are_added_and_weighed_without_old_panel_double_count(rows):
    parent = next(r for r in rows if r["id"] == "roof/aluminium/0.9mm/core-60")
    for r in rows[18:]:
        assert r["source_parent_id"] == parent["physical_definition_id"]
        assert r["physical_definition"]["source_parent_id"] == r["source_parent_id"]
        d = r["physical_definition"]["added_crossrails"]
        assert d["count"] == 8 and d["end_joint_count"] == 16
        assert d["span_m"] == 2.65 and d["nominal_new_panel_span_m"] == 1.0625
        assert d["original_ribs_retained"]
        s = {p["id"]: p for p in r["stock_parts"]}
        assert not set(s) & set(r["replacement_scope_part_ids"])
        assert s["crossrail/RHS"]["quantity"] == 8
        b, h, t = d["width_m"], d["depth_m"], d["wall_m"]
        assert s["crossrail/RHS"]["total_mass_kg"] == pytest.approx(
            (b * h - (b - 2 * t) * (h - 2 * t)) * 2.65 * 2710 * 8)
        assert len(s["crossrail/RHS"]["at_local_m"]) == 8
        assert s["crossrail/end-shoe"]["quantity"] == 16
        assert s["crossrail/end-gusset"]["quantity"] == 32
        assert s["crossrail/M8-shank"]["quantity"] == 64
        assert s["crossrail-panel/clip-plate"]["quantity"] == 48
        assert s["crossrail-panel/insert"]["quantity"] == 48
        assert r["counted_mass_kg"] == pytest.approx(parent["counted_mass_kg"] +
            r["evaluation"]["additional_stock_mass_kg"] - r["evaluation"]["displaced_additional_insert_foam_kg"])
        assert r["counted_mass_kg"] > parent["counted_mass_kg"]
        assert r["counted_mass_kg"] == pytest.approx(r["evaluation"]["panel_and_clip_mass_kg"] +
                                                     r["evaluation"]["crossrail_and_joint_mass_kg"])


def test_crossrail_force_balance_own_weight_and_independent_beam_relations(rows):
    r = rows[-1]
    f = r["evaluation"]["crossrail_fixtures"][-1]
    rail, panel = f["rail"], f["panel"]
    d = r["physical_definition"]["added_crossrails"]
    b, h, t, L = d["width_m"], d["depth_m"], d["wall_m"] * 0.9, d["span_m"]
    I = (b * h**3 - (b - 2 * t) * (h - 2 * t)**3) / 12
    q = ((1500 + r["evaluation"]["panel_and_clip_mass_kg"] * e.G / 45.05) * 1.0625 +
         r["evaluation"]["crossrail_and_joint_mass_kg"] * e.G / (8 * L))
    assert rail["line_load_N_m"] == pytest.approx(q)
    assert rail["end_reaction_N"] == pytest.approx(q * L / 2)
    assert rail["bending_stress_Pa"] == pytest.approx(q * L**2 / 8 * (h / 2) / I)
    assert rail["bending_deflection_m"] == pytest.approx(5 * q * L**4 / (384 * 69e9 * I))
    assert rail["shear_deflection_m"] == pytest.approx(q * L**2 / (8 * (69e9 / 2.66) * 2 * t * (h - 2 * t)))
    assert rail["deflection_m"] == pytest.approx(rail["bending_deflection_m"] + rail["shear_deflection_m"])
    assert f["panel_plus_rail_deflection_upper_bound_m"] == pytest.approx(rail["deflection_m"] + panel["total_deflection_m"])
    assert abs(f["force_balance_residual_N"]) < 1e-7


def test_only_deepest_crossrail_passes_both_nominal_and_reduced_wall_fixtures(rows):
    alternatives = rows[18:]
    assert [r["necessary_screen"] for r in alternatives] == ["fail", "fail", "fail", "pass"]
    marginal = alternatives[2]["evaluation"]["crossrail_fixtures"]
    assert all(f["necessary_screen"] == "pass" for f in marginal if f["wall_sensitivity_factor"] == 1)
    assert any(f["necessary_screen"] == "fail" for f in marginal if f["wall_sensitivity_factor"] == 0.9)
    for r in alternatives:
        for f in r["evaluation"]["crossrail_fixtures"]:
            assert f["panel"]["span_m"] == 1.0625
            assert f["panel"]["actual_face_strength_Pa"] is None
            assert f["rail"]["actual_joint_capacity_N"] is None
        assert r["evaluation"]["added_support_connections_and_clearance_screen"] == "unknown"
        assert not r["physical_accepted"] and not r["global_body_qualified"]
        assert r["installed_mass_kg"] is None and not r["mass_saving_credited_to_current_parent"]
    passed = alternatives[-1]
    assert passed["counted_mass_kg"] == pytest.approx(494.7175173670769)
    assert passed["conditional_counted_stock_saving_kg"] == pytest.approx(23.357482632923166)
    assert all(f["necessary_screen"] == "pass" for f in passed["evaluation"]["crossrail_fixtures"])


def test_bad_strip_inputs_and_fresh_records(rows):
    for bad in (True, 0, -1, float("nan")):
        with pytest.raises(ValueError):
            e.sandwich_strip(bad, 0.06, 22e9, 23e6, 1, 5000)
    changed = e.options(EVIDENCE_ROOT)
    changed[0]["stock_parts"][0]["total_mass_kg"] = -1
    assert e.options(EVIDENCE_ROOT)[0]["stock_parts"][0]["total_mass_kg"] > 0
