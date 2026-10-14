"""Dimensional/process scope is explicit; incomplete panel hardware stays open."""

from copy import deepcopy
import json
import math

import pytest

from engineering.design_consistency.contracts import box, part
from engineering.design_consistency.demonstrators import materials, panel_bay
from engineering.design_engine.manufacturing import compile_register, reconcile
from engineering.design_engine.manufacturing_rules import evaluate, part_bounds
from engineering.design_engine.registry import ROOT
from engineering.design_engine.exchange import definition_diff
from engineering.design_engine.contracts import fingerprint


def assembly():
    mats = materials()
    return dict(
        parts=[
            part(
                "removable",
                "steel",
                dict(role="part", primitives=[box("body", 1, 1, 0.1, [0, 0, 0])]),
                mats,
                limits=dict(minimum_wall_m=0.01),
            ),
            part(
                "obstacle",
                "steel",
                dict(role="part", primitives=[box("body", 0.2, 0.2, 0.2, [2, 0, 0])]),
                mats,
            ),
        ],
        manufacturing_plan=dict(schema="osr-manufacturing-plan/1"),
    )


def test_actual_geometry_binds_minimum_wall_and_stock_limit():
    model = assembly()
    model["manufacturing_plan"]["part_rules"] = [
        dict(
            physical_id="removable",
            stock_bounds_m=[1, 1, 0.11],
            minimum_wall_m=0.05,
            basis_reference="declared workshop fixture",
        )
    ]
    rows = evaluate(model)["checks"]
    assert (
        next(r for r in rows if r["id"] == "removable/stock-process")["state"]
        == "passed"
    )
    model["manufacturing_plan"]["part_rules"][0]["stock_bounds_m"][0] = 0.9
    assert evaluate(model)["state"] == "failed"
    model["manufacturing_plan"]["part_rules"][0]["physical_id"] = "missing"
    with pytest.raises(ValueError, match="absent"):
        evaluate(model)


def test_tool_and_removal_sweep_cannot_jump_through_installed_obstacle():
    model = assembly()
    model["manufacturing_plan"]["tool_envelopes"] = [
        dict(
            physical_id="removable",
            bounds_m=[[1.8, -0.2, -0.2], [2.2, 0.2, 0.2]],
            keepout_part_ids=["obstacle"],
            basis_reference="research socket envelope",
        )
    ]
    model["manufacturing_plan"]["removal_paths"] = [
        dict(
            physical_id="removable",
            bounds_m=[[-0.5, -0.5, -0.05], [0.5, 0.5, 0.05]],
            translation_m=[4, 0, 0],
            keepout_part_ids=["obstacle"],
            basis_reference="proposed extraction",
        )
    ]
    rows = evaluate(model)["checks"]
    assert [
        r["state"]
        for r in rows
        if "/tool_envelopes/" in r["id"] or "/removal_paths/" in r["id"]
    ] == ["failed", "failed"]
    model["manufacturing_plan"]["removal_paths"][0]["translation_m"] = [0, 2, 0]
    assert (
        next(r for r in evaluate(model)["checks"] if "/removal_paths/" in r["id"])[
            "state"
        ]
        == "passed"
    )
    model["manufacturing_plan"]["removal_paths"][0]["bounds_m"][0][0] = 0
    with pytest.raises(ValueError, match="contain"):
        evaluate(model)


def test_worst_case_tolerance_accumulation_no_rss_or_duplicate_credit():
    model = assembly()
    row = dict(
        physical_id="removable",
        nominal_clearance_m=0.001,
        required_clearance_m=0.0005,
        contributors=[
            dict(physical_id="removable", plus_minus_m=0.0003),
            dict(physical_id="obstacle", plus_minus_m=0.0003),
        ],
        basis_reference="declared hole and locating datum tolerances",
    )
    model["manufacturing_plan"]["tolerance_stacks"] = [row]
    check = next(r for r in evaluate(model)["checks"] if "/tolerance/" in r["id"])
    assert check["state"] == "failed"
    assert check["worst_case_clearance_m"] == pytest.approx(0.0004)
    row["contributors"].append(deepcopy(row["contributors"][0]))
    with pytest.raises(ValueError, match="once"):
        evaluate(model)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), True, -0.1])
def test_nonfinite_negative_or_boolean_constraints_reject(bad):
    model = assembly()
    model["manufacturing_plan"]["part_rules"] = [
        dict(
            physical_id="removable",
            stock_bounds_m=[bad, 1, 1],
            minimum_wall_m=0.01,
            basis_reference="fixture",
        )
    ]
    with pytest.raises(ValueError):
        evaluate(model)


def test_tooling_counts_are_explicit_mapped_and_never_zero_if_missing():
    model = assembly()
    register = compile_register(dict(contract=model))
    assert register["tooling"]["mould_count"] is None
    model["manufacturing_plan"]["tooling"] = [
        dict(
            id="fixture-1",
            kind="fixture",
            count=2,
            physical_part_ids=["removable"],
            basis_reference="fixture drawing",
        )
    ]
    register = compile_register(dict(contract=model))
    assert register["tooling"]["fixture_count"] == 2
    assert register["tooling"]["mould_count"] is None
    assert not register["production_released"]
    model["manufacturing_plan"]["tooling"][0]["count"] = 0
    with pytest.raises(ValueError, match="positive"):
        evaluate(model)


def test_installed_register_rejects_free_hardware_mass_and_stale_process_constraints():
    model = assembly()
    register = compile_register(dict(contract=model))
    bad = deepcopy(register)
    bad["parts"][0]["defined_mass_kg"] = 0
    with pytest.raises(ValueError, match="match actual"):
        reconcile(bad, dict(contract=model))
    bad = deepcopy(register)
    bad["dimensional_manufacturing"]["physical_definition_sha256"] = "stale"
    with pytest.raises(ValueError, match="stale dimensional"):
        reconcile(bad, dict(contract=model))


def test_curved_bounds_include_arc_extrema_and_placement():
    mats = materials()
    primitive = dict(
        id="skin",
        kind="curved-layer",
        centre_m=[0, 0, -1],
        length_m=2,
        radius_m=1,
        theta_start=-math.pi / 4,
        theta_end=math.pi / 4,
        z_lower_m=0,
        z_upper_m=0.01,
    )
    p = part(
        "curve",
        "gfrp",
        dict(role="curved skin", primitives=[primitive]),
        mats,
        placement=dict(
            translation_m=[3, 0, 0], rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        ),
    )
    lo, hi = part_bounds(p)
    assert [lo[0], hi[0]] == [2, 4]
    assert hi[2] == pytest.approx(0.01)
    assert hi[1] == pytest.approx(1.01 / math.sqrt(2))


@pytest.mark.parametrize("crown,aperture", [(0, True), (0.05, False)])
def test_actual_panel_inventory_has_explicit_seal_retention_and_head_mass_gaps(
    crown, aperture
):
    config = json.loads(
        (ROOT / "engineering/composite_panels/config/development.json").read_text()
    )
    model = panel_bay(config, crown=crown, aperture=aperture)
    definition = dict(contract=model)
    register = reconcile(compile_register(definition), definition)
    detail = register["panel_installed_details"]
    assert (
        detail["defined_clip_count"]
        == detail["defined_clip_bolt_count"]
        == detail["attachment_site_count"]
    )
    assert (
        len(detail["missing_clip_head_part_ids"]) == detail["defined_clip_bolt_count"]
    )
    assert detail["defined_insert_count"] == (
        0 if crown else detail["attachment_site_count"]
    )
    assert detail["perimeter_seal"]["required_path_length_m"] > 2 * (
        model["panel_parameters"]["width_m"] + model["panel_parameters"]["height_m"]
    )
    assert detail["perimeter_seal"]["installed_mass_kg"] is None
    assert detail["secondary_retention"] is None
    assert not detail["complete_installed_kit"]
    assert register["dimensional_manufacturing"]["state"] == "unknown"
    assert not register["physical_release"]


def test_desktop_process_plan_change_returns_adverse_feedback_without_baseline_write():
    config = json.loads(
        (ROOT / "engineering/composite_panels/config/development.json").read_text()
    )
    original = panel_bay(config)
    original_sha = fingerprint(original)
    proposed = deepcopy(original)
    proposed["manufacturing_plan"] = dict(
        schema="osr-manufacturing-plan/1",
        part_rules=[
            dict(
                physical_id=original["parts"][0]["id"],
                stock_bounds_m=[10, 10, 10],
                minimum_wall_m=0.01,
                basis_reference="future controlled workshop requirement",
            )
        ],
    )
    result = definition_diff(original, proposed)
    assert fingerprint(original) == original_sha == result["original_sha256"]
    assert result["proposed_sha256"] == fingerprint(proposed)
    assert result["changed_definition"]
    assert result["changed"] == []
    assert result["dimensional_manufacturing"]["state"] == "failed"
    assert result["panel_installed_details"]["complete_installed_mass_kg"] is None
    assert not result["baseline_overwrite_permitted"]
    assert not result["physical_release"]
    assert result["candidate_draft"] == proposed


def test_desktop_process_plan_rejects_fabricated_physical_id_and_release_authority():
    config = json.loads(
        (ROOT / "engineering/composite_panels/config/development.json").read_text()
    )
    original = panel_bay(config)
    proposed = deepcopy(original)
    proposed["manufacturing_plan"] = dict(
        schema="osr-manufacturing-plan/1", production_released=True
    )
    with pytest.raises(ValueError, match="unknown manufacturing"):
        definition_diff(original, proposed)
    proposed["manufacturing_plan"] = dict(
        schema="osr-manufacturing-plan/1",
        part_rules=[
            dict(
                physical_id="absent",
                stock_bounds_m=[1, 1, 1],
                minimum_wall_m=0.01,
                basis_reference="fixture",
            )
        ],
    )
    with pytest.raises(ValueError, match="absent"):
        definition_diff(original, proposed)
